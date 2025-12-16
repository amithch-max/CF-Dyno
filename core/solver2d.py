import numpy as np

def solve_lbm_frame(F, obstacle, omega, steps_per_frame=20):
    ny, nx, nl = F.shape
    idxs = np.arange(nl)
    cxs = np.array([0, 0, 1, 1, 1, 0, -1, -1, -1])
    cys = np.array([0, 1, 1, 0, -1, -1, -1, 0, 1])
    weights = np.array([4/9, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36, 1/9, 1/36])

    for _ in range(steps_per_frame):
        for j, cx, cy in zip(idxs, cxs, cys):
            F[:, :, j] = np.roll(F[:, :, j], cx, axis=1)
            F[:, :, j] = np.roll(F[:, :, j], cy, axis=0)

        bndryF = F[obstacle, :]
        bndryF = bndryF[:, [0, 5, 6, 7, 8, 1, 2, 3, 4]]

        rho = np.sum(F, 2)
        ux = np.sum(F * cxs, 2) / rho
        uy = np.sum(F * cys, 2) / rho

        Feq = np.zeros(F.shape)
        for j, cx, cy, w in zip(idxs, cxs, cys, weights):
            term = (cx*ux + cy*uy)
            Feq[:, :, j] = rho * w * (1 + 3*term + 4.5*(term**2) - 1.5*(ux**2 + uy**2))

        F += -(1.0 / omega) * (F - Feq)
        F[obstacle, :] = bndryF

    rho = np.sum(F, 2)
    ux = np.sum(F * cxs, 2) / rho
    uy = np.sum(F * cys, 2) / rho
    velocity_mag = np.sqrt(ux**2 + uy**2)
    return F, velocity_mag
