import numpy as np
import shutil
import os


# Output directory
odir = 'out'


# Options added to radmc3d.inp
options = {
    'scattering_mode_max': 0,  # 0 = no scattering
    # 'setthreads': 8  # NOTE: will fail if there are not enough threads
}


#### Example dummy disk model -- load your own! ########################
# Required data: edge_r, edge_th, edge_phi, temperature, vr, vth, vphi,
#                molecules, dust_species
# 3D arrays should have the layout arr[ir, ith, iphi]
# Units are in CGS
########################################################################

AU = 14959787069100 # cm
edge_r = np.linspace(0.5, 5, 100) * AU
edge_th = np.linspace(5 * np.pi / 12, 7 * np.pi / 12, 55)  # NOTE: edge_th must include pi/2
edge_phi = np.linspace(0, 2 * np.pi, 150)

rr, tt, pp = np.meshgrid(
    (edge_r[1:] + edge_r[:-1])/2,
    (edge_th[1:] + edge_th[:-1])/2,
    (edge_phi[1:] + edge_phi[:-1])/2,
    indexing='ij'
)


temperature = 250 * (rr/AU)**-0.5
vr = np.zeros_like(rr)
vth = np.zeros_like(rr)
vphi = np.sqrt(1.33e26 / rr)


matter_density = (
    1e-10 * (rr/AU)**-2 *
    np.exp(-((tt - np.pi/2) / 0.1)**2) *   # higher density at midplane
    (1 - np.exp(-((rr/AU - 2) / 0.1)**2))  # gap
)

mu = 2.35  # Mean molecular weight of the gas
gas_num_den = 6.022e23 * matter_density / mu

# The molecules dict has an entry for each molecule to include lines of,
# with the value being the number density of the molecule in cm^-3
# Assuming Python >= 3.7, the order of this dictionary corresponds to
# imolspec indices, eg imolspec 1 is the first entry in this dictionary.
# Usually there's no need to have more than one entry though.
molecules = {
    # See https://www.aanda.org/articles/aa/full_html/2021/01/aa37776-20/aa37776-20.html
    # 'co': 6e-5 * gas_num_den,
    '13co': 2.5e-6 * gas_num_den,
    # 'c18o': 2.0e-7 * gas_num_den,
}


# The dust_species dict has an entry for each dust species, with the
# value being density in g/cm^3
dust_species = {
    'silicate': 0.01 * matter_density
}


if __name__ == '__main__':
    os.makedirs(odir, exist_ok=True)

    nr = len(edge_r) - 1
    nth = len(edge_th) - 1
    nphi = len(edge_phi) - 1
    nrcells = nr * nth * nphi

    with open(f'{odir}/radmc3d.inp', 'w') as f:
        for key, value in options.items():
            f.write(f'{key} = {value}\n')

    with open(f'{odir}/amr_grid.inp', 'w') as f:
        f.write(f'1\n')    # iformat
        f.write(f'0\n')    # grid style: 0 = regular
        f.write(f'100\n')  # coordsystem: 100 = spherical
        f.write(f'0\n')    # gridinfo: 0 = off
        f.write(f'1 1 1\n')
        f.write(f'{nr} {nth} {nphi}\n')
        f.write(' '.join(map(str, edge_r)) + '\n')
        f.write(' '.join(map(str, edge_th)) + '\n')
        f.write(' '.join(map(str, edge_phi)) + '\n')

    with open(f'{odir}/lines.inp', 'w') as f:
        f.write(f'2\n')  # iformat
        f.write(f'{len(molecules)}\n')
        for mol in molecules:
            shutil.copy(f'molecule_{mol}.inp', odir)
            f.write(f'{mol}   leiden   0   0   0\n')

    with open(f'{odir}/dustopac.inp', 'w') as f:
        f.write('2\n')  # iformat
        f.write(f'{len(dust_species)}\n')
        for spec in dust_species:
            shutil.copy(f'dustkappa_{spec}.inp', odir)
            f.write('-----------------------------\n')
            f.write('1\n')  # inputstyle: 1 = dustkappa_*.inp
            f.write('0\n')  # iquantum: 0 = thermal grains
            f.write(f'{spec}\n')

    for mol, mol_den in molecules.items():
        with open(f'{odir}/numberdens_{mol}.inp', 'w') as f:
            f.write(f'1\n')  # iformat
            f.write(f'{nrcells}\n')
            for iphi in range(nphi):
                for ith in range(nth):
                    for ir in range(nr):
                        f.write(f'{mol_den[ir, ith, iphi]}\n')

    with open(f'{odir}/gas_temperature.inp', 'w') as f:
        f.write(f'1\n')  # iformat
        f.write(f'{nrcells}\n')
        for iphi in range(nphi):
            for ith in range(nth):
                for ir in range(nr):
                    f.write(f'{temperature[ir, ith, iphi]}\n')

    with open(f'{odir}/gas_velocity.inp', 'w') as f:
        f.write(f'1\n')  # iformat
        f.write(f'{nrcells}\n')
        for iphi in range(nphi):
            for ith in range(nth):
                for ir in range(nr):
                    idx = (ir, ith, iphi)
                    f.write(f'{vr[idx]} {vth[idx]} {vphi[idx]}\n')

    with open(f'{odir}/dust_density.inp', 'w') as f:
        f.write(f'1\n')  # iformat
        f.write(f'{nrcells}\n')
        f.write(f'{len(dust_species)}\n')
        for spec_den in dust_species.values():
            for iphi in range(nphi):
                for ith in range(nth):
                    for ir in range(nr):
                        f.write(f'{spec_den[ir, ith, iphi]}\n')

    with open(f'{odir}/dust_temperature.dat', 'w') as f:
        f.write(f'1\n')  # iformat
        f.write(f'{nrcells}\n')
        f.write(f'{len(dust_species)}\n')
        for spec in dust_species:
            for iphi in range(nphi):
                for ith in range(nth):
                    for ir in range(nr):
                        # Use same temperature for all species
                        f.write(f'{temperature[ir, ith, iphi]}\n')


    # radmc3d always demands a wavelength_micron.inp file, even though
    # it is unused for generating images (at least without scattering).
    wl_micron = np.logspace(-1, 4, 100)
    with open(f'{odir}/wavelength_micron.inp', 'w') as f:
        f.write(f'{len(wl_micron)}\n')
        for wl in wl_micron:
            f.write(f'{wl}\n')
