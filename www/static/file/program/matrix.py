from numpy import *
import numpy as np
import copy

def swap(A, i, j):
    tmp = copy.copy(A[i])
    A[i] = A[j]
    A[j] = tmp

def swapcol(A, i, j):
    tmp = copy.copy(A[:, i])
    A[:, i] = A[:, j]
    A[:, j] = tmp

# row i reduce row base
def row_reduce(A, base, i, coef):
    for s in range(0, A.shape[1]):
        A[i,s] = A[i,s] - A[base,s]*coef
    pass

# judge vector is vertical or straight
def isvertical(V):
    if V.shape[0] == 1:
        return 1
    return 0

# vector norm
def vector_norm(V):
    if isvertical(V):
        return sqrt(V*V.T)[0,0]
    return sqrt(V.T*V)[0,0]

def row_unit_vector(n, x):
    unit = mat(zeros((1,n)))
    unit[x-1] = 1
    return unit

def col_unit_vector(n, x):
    unit = mat(zeros((n,1)))
    unit[x-1] = 1
    return unit

def get_float_matrix(A):
    [m,n] = A.shape
    B = mat(zeros((m,n)))
    for i in arange(m):
        for j in arange(n):
            B[i,j] = A[i,j]
    return B


# ____________________ LU factorization _________________________
def adjust(L, U, P, i, m):
    log = i
    for j in range(i,m):
        if abs(U[j,i]) > abs(U[log,i]):
            log = j
    swap(L, i, log)
    swap(U, i, log)
    swap(P, i, log)


def LU(A):
    [m,n] = A.shape
    if m != n:
        print("error m != n")
        return
    L = mat(zeros((m,m)))
    U = get_float_matrix(A)
    P = mat(eye(m,m))

    L[0,0] = 1
    adjust(L, U, P, 0, m)

    for i in range(0,m):
        L[i,i] = 1
        for j in range(i+1,m):
            L[j,i] = U[j,i]/U[i,i]
            row_reduce(U, i, j, L[j,i])
        if i < m-1:
            adjust(L, U, P, i+1, m)

    return [L, U, P]


# _______________________ QR_Gram_Schmidt ___________________
def QR_Gram_Schmidt(A):
    [m,n] = A.shape
    Q = get_float_matrix(A)
    R = mat(zeros((m,m)))
    for i in arange(n):
        for j in arange(i):
            R[j,i] = Q[:,i].T * Q[:,j]
        for j in arange(i):
            Q[:,i] = Q[:,i] - Q[:,j]*R[j,i]
        R[i,i] = vector_norm(Q[:,i])
        Q[:,i] = Q[:,i] / R[i,i]
    return [Q,R]

# ___________________ Householder reduction __________________________
def householder_reduction(B):
    A = get_float_matrix(B)
    [m,n] = A.shape
    if m==1:
        print("error input matrix size should be bigger then 1")
        return B
    e1 = col_unit_vector(m,1)
    u1 = A[:,0] - vector_norm(A[:,0])*e1
    R1 = mat(eye(m,m)) - 2 * u1 * u1.T / (u1.T * u1)
    C = R1 * A
    if m==2:
        return R1
    R2sub = householder_reduction(C[1:m,1:n])
    f = mat(zeros((1,m-1)))
    R2 = vstack((f,R2sub))
    R2 = hstack((e1,R2))
    return R2 * R1

# ___________________ Givens reduction ___________________
def givens_reduction(B):
    A = get_float_matrix(B)
    [m,n] = A.shape
    if m==1:
        print("error input matrix size should be bigger then 1")
        return B
    P1 = mat(eye(m,m))
    for i in range(1,m):
        Pi = mat(eye(m,m))
        xi = A[0,0]
        xj = A[i,0]
        A[0,0] = sqrt(xi*xi + xj*xj)
        A[i,0] = 0
        Pi[0,0] = Pi[i,i] = xi/A[0,0]
        Pi[0,i] = xj/A[0,0]
        Pi[i,0] = -1*xj/A[0,0]
        P1 = Pi * P1
    C = P1 * A
    if m == 2:
        return P1
    P2sub = givens_reduction(C[1:m,1:n])
    f = mat(zeros((1,n-1)))
    e1 = col_unit_vector(m,1)
    P2 = vstack((f,P2sub))
    P2 = hstack((e1,P2))
    return P2*P1


def factorization(A, t):
    if t==0:
        print("LU factorization")
        [L,U,P] = LU(A)
        print("L:\n", L)
        print("U:\n", U)
        print("P:\n", P)
    elif t==1:
        print("QR factorization")
        [Q,R] = QR_Gram_Schmidt(A)
        print("Q:\n", Q)
        print("R:\n", R)
    elif t==2:
        print("household reduction")
        P = householder_reduction(A)
        print("P:\n", P)
        print("T:\n", P*A)
    elif t==3:
        print("givens reduction")
        P = givens_reduction(A)
        print("P:\n", P)
        print("T:\n", P*A)
    else:
        print("please input factorization type from 0 to 3")

A = mat([[1,4,5],[4,18,26],[3,16,30]])
factorization(A, 0)
