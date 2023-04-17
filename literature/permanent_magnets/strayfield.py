# -*- coding: utf-8 -*-
"""
Class to calculate magnetic stray field of uniform rectangular prisms

for math:
    Calculation of the magnetic stray field of a uniaxial magnetic domain
R. Engel-Herbert, and T. Hesjedal
    https://doi.org/10.1063/1.1883308

@author: adoll
@version 2023 for pyhton3
"""

#import matplotlib.pyplot as plt
import numpy as np
import itertools
from collections import namedtuple
import copy
#from mayavi import mlab

from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

import matplotlib.pyplot as plt

class strayfield(object):
    # constructor: load data
    def __init__(self, ):
        self.n_samples = 0
        self.smp = []
        self.smp_struct = namedtuple('smp_struct', 'M dim zro name calc col')
        
    # add sample to the container
    def add_sample(self,sample_mag, sample_dim, sample_zero = np.zeros(3), name = 'foo', col = 'r'):
        smp = self.smp_struct(np.asarray(sample_mag), np.asarray(sample_dim)*1e-6, np.asarray(sample_zero)*1e-6, name, True, col)
        self.smp.append(smp)
        self.n_samples += 1
        
    # remove sample (all ocurrences of name)
    def rem_sample(self,name):
        ii = len(self.smp) - 1
        while ii > -1:
            if self.smp[ii].name == name:
                self.smp.pop(ii)
                self.n_samples -= 1
            ii -= 1
            
    # enable/disable sample for calculation
    def set_calc(self, name, calc = True):
        for ii in np.arange(len(self.smp)):
            if self.smp[ii].name == name:
                act = self.smp[ii]
                smp = self.smp_struct(act.M, act.dim, act.zro, act.name, calc, act.col)
                self.smp[ii] = smp
            
    # set target volume/area/line (inputs in microns)
    def set_target(self, targ_elong, targ_zero,targ_discr):
        t0 = np.asarray(targ_zero) # zero point of target
        tl = np.asarray(targ_elong) # elongation of target
        td = np.asarray(targ_discr) # discretization
        
        steps = (tl/td) # number of steps
        
        # get dimension of target
        zro_ids = np.where(tl<1e-12)[0]
        nzro_ids = np.where(tl>1e-12)[0]
        
        self.targ_dim = 3-len(zro_ids)
        self.zro_ids = zro_ids
        self.nzro_ids = nzro_ids
        
        # span x,y,z
        tx = np.linspace(-tl[0]/2,tl[0]/2,int(steps[0]+1)) + t0[0]
        ty = np.linspace(-tl[1]/2,tl[1]/2,int(steps[1]+1)) + t0[1]
        tz = np.linspace(-tl[2]/2,tl[2]/2,int(steps[2]+1)) + t0[2]
        
        # generate 'general' coordinates for computation
        if self.targ_dim == 3:
            tX,tY,tZ = np.meshgrid(tx, ty, tz, indexing='ij' )
            Bstray = np.zeros((len(tx),len(ty),len(tz),3))
        elif self.targ_dim == 2:
            # get the non-sweptaxis for the 2D case
            if zro_ids == 0:
                tX = tx.copy()
                tY,tZ = np.meshgrid(ty, tz, indexing='ij' )
                Bstray = np.zeros((len(ty),len(tz),3))
            elif zro_ids == 1:
                tY = ty.copy()
                tX,tZ = np.meshgrid(tx, tz, indexing='ij' )
                Bstray = np.zeros((len(tx),len(tz),3))
            else:
                tZ = tz.copy()
                tX,tY = np.meshgrid(tx, ty, indexing='ij' )
                Bstray = np.zeros((len(tx),len(ty),3))
        else:
            tX = tx.copy()
            tY = ty.copy()
            tZ = tz.copy()
            if self.targ_dim == 1:
                Bstray = np.zeros((max([len(tx), len(ty), len(tz)]),3))
            else:
                Bstray = np.zeros(3)
                
        # convert microns to meters
        tX *= 1e-6      
        tY *= 1e-6
        tZ *= 1e-6
        
        self.Bstray = Bstray
        self.tC = [tX, tY, tZ]
        self.tc = [tx, ty, tz]
        
    # to reset calculation result
    def reset_Bstray(self):
        self.Bstray = 0.0* self.Bstray

        
    def calculate(self):
        
        mu0 = 4*np.pi*1e-7        
        prefac = mu0/4/np.pi

        # loop through geometry
        for ii_sample in np.arange(self.n_samples):
            
            if self.smp[ii_sample].calc == False:
                continue
            
            barC = self.smp[ii_sample].dim
            barZ = self.smp[ii_sample].zro
            M = self.smp[ii_sample].M
            
            
            tC = copy.deepcopy(self.tC)
            
            # adjust the target coordinates in case of displaced sample
            for ii_targetshift in np.arange(3):
                tC[ii_targetshift] -= barZ[ii_targetshift]
                
                
            Bstray_comp = np.zeros_like(self.Bstray)
            
            # loop through axes
            for coor_idx in np.arange(3):
            
                if M[coor_idx] != 0:
                    # permutation order  (keep new system right handed ...)
                    perm = np.roll([2,0,1],-coor_idx)
                    invperm = np.roll([1,2,0],coor_idx)
                    
                    for kk, ll, mm in itertools.product([1,2],[1,2],[1,2]):
                        xx = tC[perm[0]] + (-1)**kk*(barC[perm[0]]/2.0)
                        yy = tC[perm[1]] + (-1)**ll*(barC[perm[1]]/2.0)
                        zz = tC[perm[2]] + (-1)**mm*(barC[perm[2]]/2.0)
                        thatsqrt = np.sqrt(xx**2+yy**2+zz**2)
                        Bstray_comp[...,0] += (-1)**(kk+ll+mm) * np.log( zz + thatsqrt)
                        Bstray_comp[...,1] -= (-1)**(kk+ll+mm) * yy * xx / np.abs(yy) / np.abs(xx) * np.arctan( np.abs(xx) * zz / np.abs(yy) / thatsqrt)
                        Bstray_comp[...,2] += (-1)**(kk+ll+mm) * np.log( xx + thatsqrt)
                        
                    Bstray_comp *= prefac*M[coor_idx]
                    
                    self.Bstray += Bstray_comp[...,invperm]


    def plot_sample(self, fignum = 300):
                
        fig = plt.figure(fignum)
        plt.clf()
        ax = fig.gca(projection='3d')
        # ax.set_aspect("equal")
        
        # initialization of boundcoord for geometry plotting
        self.boundcoord = np.zeros((3,2))
        
        # loop through geometry
        for ii_sample in np.arange(self.n_samples):
            
            barC = self.smp[ii_sample].dim * 1e6
            barZ = self.smp[ii_sample].zro * 1e6
            
            mlt = np.array([-0.5, 0.5])
            x_range = mlt*barC[0]+barZ[0]
            y_range = mlt*barC[1]+barZ[1]
            z_range = mlt*barC[2]+barZ[2]
            
            self.rect_prism(x_range, y_range, z_range, ax, self.smp[ii_sample].col)
            
            self.update_boundcoords(x_range, y_range, z_range)
            
        plt.show()
        
        # make some useful aspect window
        max_id = self.boundcoord[:,1].argmax()
        min_id = self.boundcoord[:,0].argmin()
                
        
        ax.set_xlim3d(self.boundcoord[min_id, 0], self.boundcoord[max_id, 1])
        ax.set_ylim3d(self.boundcoord[min_id, 0], self.boundcoord[max_id, 1])
        ax.set_zlim3d(self.boundcoord[min_id, 0], self.boundcoord[max_id, 1])
                
        self.ax_3d = ax
        
        
    def plot_sample_and_target(self, fignum = 300):
        # first plot the sample
        self.plot_sample(fignum = fignum)
        
        # now add the target domain
        x_range = [self.tc[0][0], self.tc[0][-1]]
        y_range = [self.tc[1][0], self.tc[1][-1]]
        z_range = [self.tc[2][0], self.tc[2][-1]]
        
        self.rect_prism(x_range, y_range, z_range, self.ax_3d, col = 'g')
        
        self.update_boundcoords(x_range, y_range, z_range)
     
    # updates boundary coordinates according to xyz ranges of new rect_prism to add
    def update_boundcoords(self, x_range, y_range, z_range):
    
        # initialized?
        if not np.any(self.boundcoord != 0):
            self.boundcoord[:,0] = np.array([x_range[0], y_range[0], z_range[0]])
            self.boundcoord[:,1] = np.array([x_range[1], y_range[1], z_range[1]])
        else:
            if self.boundcoord[0,1] < x_range[1]: self.boundcoord[0,1] = x_range[1]
            if self.boundcoord[1,1] < y_range[1]: self.boundcoord[1,1] = y_range[1]
            if self.boundcoord[2,1] < z_range[1]: self.boundcoord[2,1] = z_range[1]
            if self.boundcoord[0,0] > x_range[0]: self.boundcoord[0,0] = x_range[0]
            if self.boundcoord[1,0] > y_range[0]: self.boundcoord[1,0] = y_range[0]
            if self.boundcoord[2,0] > z_range[0]: self.boundcoord[2,0] = z_range[0]             
        
        
    # draw cube function from stackexchange
    def rect_prism(self, x_range, y_range, z_range, ax, col = 'r'):
#        xx, yy = np.meshgrid(x_range, y_range)
#        ax.plot_wireframe(xx, yy, z_range[0], color=col)
#        ax.plot_surface(xx, yy, z_range[0], color=col, alpha=0.2)
#        ax.plot_wireframe(xx, yy, z_range[1], color=col)
#        ax.plot_surface(xx, yy, z_range[1], color=col, alpha=0.2)
#    
#    
#        yy, zz = np.meshgrid(y_range, z_range)
#        ax.plot_wireframe(x_range[0], yy, zz, color=col)
#        ax.plot_surface(x_range[0], yy, zz, color=col, alpha=0.2)
#        ax.plot_wireframe(x_range[1], yy, zz, color=col)
#        ax.plot_surface(x_range[1], yy, zz, color=col, alpha=0.2)
#    
#        xx, zz = np.meshgrid(x_range, z_range)
#        ax.plot_wireframe(xx, y_range[0], zz, color=col)
#        ax.plot_surface(xx, y_range[0], zz, color=col, alpha=0.2)
#        ax.plot_wireframe(xx, y_range[1], zz, color=col)
#        ax.plot_surface(xx, y_range[1], zz, color=col, alpha=0.2)   

        # new method using polycollection
        points = []
        points.append([x_range[0], y_range[0], z_range[0]])
        points.append([x_range[1], y_range[0], z_range[0]])
        points.append([x_range[1], y_range[1], z_range[0]])
        points.append([x_range[0], y_range[1], z_range[0]])
        points.append([x_range[0], y_range[0], z_range[1]])
        points.append([x_range[1], y_range[0], z_range[1]])
        points.append([x_range[1], y_range[1], z_range[1]])
        points.append([x_range[0], y_range[1], z_range[1]])
        
        points = np.array(points)
        
        edges = [
            [points[0], points[1], points[5], points[4]],
            [points[1], points[2], points[6], points[5]],
            [points[2], points[3], points[7], points[6]],
            [points[3], points[0], points[4], points[7]],
            [points[0], points[1], points[2], points[3]],
            [points[4], points[5], points[6], points[7]]
        ]


    
        faces = Poly3DCollection(edges, linewidths=1, edgecolors=col)
        faces.set_alpha(0.25)
        faces.set_facecolor(col)
    
        ax.add_collection3d(faces)
    
        # Plot the points themselves to force the scaling of the axes
        ax.scatter(points[:,0], points[:,1], points[:,2], s=0)
    
        # ax.set_aspect('equal')