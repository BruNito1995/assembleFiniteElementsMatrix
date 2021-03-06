import sympy as sym
import numpy as np 

def basis(d, point_distribution='uniform', symbolic=False):
    """
    Return all local basis function phi as functionsof the local point X in a 1D
    element with 1+d nodes.
    """
    X = sym.symbols('X')
    if d == 0:
        phi_sym = [1]

    else:
        if point_distribution == 'uniform':
            if symbolic:
                # compute symbolic nodes
                h = sym.Rational(1,d)
                nodes = [2*i*h -1 for i in range(d+1)]
            else:
                nodes = np.linspace(-1, 1, d+1)
        elif point_distribution == 'Chebyshev':
            nodes = Chebyschev_nodes(-1,1,d)
        
        phi_sym = [Lagrange_polynomial(X, r, nodes) for r in range(d+1)]

    phi_num = [sym.lambdify([X], phi_sym[r], modules='numpy') for r in range(d+1)]

    return phi_sym if symbolic else phi_num


def Lagrange_polynomial(x, i, points):
    p = 1
    for k in range(len(points)):
        if k != i:
            p *= (x - points[k])/(points[i] - points[k])

    return p

def element_matrix(phi, Omega_e, symbolic = True):
    n = len(phi)
    A_e = sym.zeros(n,n)
    X = sym.Symbol('X')
    if symbolic:
        h = sym.Symbol('h')
    else:
        h = Omega_e[1] - Omega_e[0]
    detJ = h/2 # dx/dX

    for r in range(n):
        for s in range(r,n):
            A_e[r, s] = sym.integrate(phi[r]*phi[s]*detJ, (X, -1, 1))
            A_e[s, r] = A_e[r, s]
    return A_e

def element_vector(f, phi, Omega_e, symbolic = True):
    n = len(phi)
    b_e = sym.zeros(n,1)
    X = sym.Symbol('X')
    if symbolic:
        h = sym.Symbol('h')
    else:
        h = Omega_e[1] - Omega_e[0]
    x = (Omega_e[0] + Omega_e[1])/2 + h/2*X
    f = f.subs('x',x)
    detJ = h/2
    for r in range(n):
        if symbolic:
            I = sym.integrate(f*phi[r]*detJ, (X, -1, 1))
        if not symbolic or isinstance(I, sym.Integral):
            h = Omega_e[1] - Omega_e[0]
            detJ = h/2
            integrand = sym.lamdify([X], f*phi[r]*detJ, 'mpmath')
            I = mpmath.quad(integrand, [.1,1])
        b_e[r] = I
        
    return b_e

def assemble(nodes, elements, phi , f, symbolic = True):
    N_n, N_e = len(nodes), len(elements)
    if symbolic:
        A = sym.zeros(N_n, N_n)
        b = sym.zeros(N_n, 1)
    else:
        A = np.zeros((N_n,N_n))
        b = np.zeros((N_n,1))
    
    for e in range(N_e):
        Omega_e = nodes[elements[e][0]], nodes[elements[e][-1]]

        A_e = element_matrix(phi, Omega_e, symbolic)
        b_e = element_vector(f, phi, Omega_e, symbolic)

        for r in range(len(elements[e])):
            for s in range(len(elements[e])):
                A[elements[e][r],elements[e][s]] += A_e[r,s]
            b[elements[e][r]] += b_e[r]

    return A, b