def sigma(i, j):
    return 0 if i > j else 1

def RK4(F,G,x,v,h):
    k1 = F(x,v)*h
    l1 = G(x,v)*h   

    k2 = F(x+k1/2.0,v+l1/2.0)*h
    l2 = G(x+k1/2.0,v+l1/2.0)*h

    k3 = F(x+k2/2.0,v+l2/2.0)*h
    l3 = G(x+k2/2.0,v+l2/2.0)*h

    k4 = F(x+k3,v+l3)*h
    l4 = G(x+k3,v+l3)*h       

    x = x+(k1+2.0*k2+2.0*k3+k4)/6.0
    v = v+(l1+2.0*l2+2.0*l3+l4)/6.0
    
    return x, v