# test strayfield class
import strayfield

import numpy as np
import matplotlib.pyplot as plt


# magnetism
mu0 = 4*np.pi*1e-7

Ms1 = 1.44 / mu0 *1.006# N52 grade (to get closer to the values of tayler)
Ms1 = 1.44 / mu0 # N52 grade
Ms2 = 1.37 / mu0 # the slighlty more coercive N48SH graders

# magnetizations
M1_x = np.array([Ms1,0,0])
M1_y = np.array([0, Ms1,0])

M2_x = np.array([Ms2,0,0])
M2_y = np.array([0, Ms2,0])

# sample geometry
i_mm = 25.4
a = 0.5 * i_mm
b = a
c = 2 * i_mm

sample_elong =  [a,  b,  c]

gap_x  = 0.3 * i_mm

# generate positions and magnetizations given N
block_2 = []
block_4 = []
block_8 = []
block_24 = []

col1 = 'r'
col2 = 'b'


pos_x = 0
pos_y = 0
pos_z = 0

# populate, see fig1 of JMR277 of Tayler
for ii in range(24):
    # the central ones that are in any design
    if ii < 2:
        off_x = (gap_x+a)/2
        act_pos = [pos_x-off_x + ii*2*off_x, pos_y, pos_z]
        
        block_2.append((M1_x, act_pos, col1))
        block_4.append((M1_x, act_pos, col1))
        block_8.append((M1_x, act_pos, col1))
        block_24.append((M1_x, act_pos, col1))
        continue
    
    # the left right outer ones
    if ii < 4:
        off_y = b
        act_pos = [pos_x, pos_y-off_y + np.mod(ii,2)*2*off_y, pos_z]
        block_4.append((-M1_x, act_pos, col1))
        block_8.append((-M1_x, act_pos, col1))
        block_24.append((-M2_x, act_pos, col2))
        continue
    
    # the remaining ones of the 8 block
    if ii < 8:
        
        off_x = a
        off_y = b
        id_x = np.mod(ii,2)
        id_y = np.mod(ii,4)>>1
        act_pos = [pos_x-off_x + id_x*2*off_x, pos_y-off_y + id_y*2*off_y, pos_z]
        
        sign = (-1)**(id_x+id_y)
        
        block_8.append((sign*M1_y, act_pos, col1))
        block_24.append((sign*M2_y, act_pos, col2))
        
        continue
        
    # now the rest of block_24
    if ii < 12:
        # the four pointing up
        off_x = 2*a
        off_y = b
        id_x = np.mod(ii,2)
        id_y = np.mod(ii,4)>>1
        act_pos = [pos_x-off_x + id_x*2*off_x, pos_y-off_y + id_y*2*off_y, pos_z]
                
        block_24.append((M1_x, act_pos, col1))
        
        continue
    
    if ii < 16:
        # the four at the outer edges
        off_x = 2*a
        off_y = 2*b
        id_x = np.mod(ii,2)
        id_y = np.mod(ii,4)>>1
        act_pos = [pos_x-off_x + id_x*2*off_x, pos_y-off_y + id_y*2*off_y, pos_z]
                
        sign = (-1)**(id_x+id_y)
                
        block_24.append((sign*M2_y, act_pos, col2))
        
        continue
        
    if ii < 20:
        # four more
        off_x = a
        off_y = 2*b
        id_x = np.mod(ii,2)
        id_y = np.mod(ii,4)>>1
        act_pos = [pos_x-off_x + id_x*2*off_x, pos_y-off_y + id_y*2*off_y, pos_z]
                
        sign = (-1)**(id_x+id_y)
        
        block_24.append((sign*M2_y, act_pos, col2))
        
        continue
        
    if ii < 22:
        # the two weak ones
        off_x = 0
        off_y = 2*b
        id_y = np.mod(ii,2)
        act_pos = [pos_x, pos_y-off_y + id_y*2*off_y, pos_z]
        
        block_24.append((-M2_x, act_pos, col2))
        
        continue
    
    if ii < 24:
        # the two strong ones
        off_x = (gap_x+a)/2+a
        id_x = np.mod(ii,2)
        act_pos = [pos_x-off_x + id_x*2*off_x, pos_y, pos_z]
        
        block_24.append((M1_x, act_pos, col1))
        
        continue
        
    



# target specification
target_elong = [ 0, 7/8*a,  c]
target_zero  = [ 0, 0,  0]
target_discr = [ 0.5, 0.5, 0.5]



stray = strayfield.strayfield();

for ii, block in enumerate(block_24):
    stray.add_sample(block[0], sample_elong, block[1], ['el{:}'.format(ii)], col=block[2])
        
stray.set_target(target_elong, target_zero, target_discr);

stray.plot_sample_and_target()
plt.gca().view_init(elev=-91, azim=0)
plt.gcf()

stray.calculate()


#%% get the central field for all the designs
target_ref_elong = [0, 1e-3, 0]
target_ref_discr = [1e-4, 1e-4, 1e-4]

for act_block in [block_2, block_4, block_8, block_24]:
    
    stray_mx = strayfield.strayfield();
    
    for ii, block in enumerate(act_block):
        stray_mx.add_sample(block[0], sample_elong, block[1], ['el{:}'.format(ii)], col=block[2])
            
    # stray_mx.set_target(target_elong, target_zero, target_discr);
    stray_mx.set_target(target_ref_elong, target_zero, target_ref_discr);
    
    
    stray_mx.calculate()
    
    B_abs = np.sqrt(stray_mx.Bstray[:,0]**2+stray_mx.Bstray[:,1]**2+stray_mx.Bstray[:,2]**2)
    
    print('Bx = {}, Babs = {}'.format(stray_mx.Bstray[:,0].max(), B_abs.max()) )


#%% visualize

cmin = np.nanmin(stray.Bstray)
cmax = np.nanmax(stray.Bstray)
cvec = np.arange(int(np.floor(cmin)),int(np.ceil(cmax)),10)

# logarithmic spaced color vector
#cvec = np.logspace(0,np.log10(cmax),10)
#n_id = np.where(cvec<=abs(cmin))[0]
#cvec = np.append(np.append(np.flipud(-cvec[n_id]),0),cvec)

# custom color vectors..
#cvec = np.linspace(10,40,16)
#cvec = np.linspace(35,65,16)

clabelsize = 4 # for plot exports
clabelsize = 12

data = stray.Bstray[:,:,0]
#data=np.transpose(data2)

plt.figure(21)
plt.clf()
CS = plt.contour(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data , cmap=plt.get_cmap('winter'))
plt.clabel(CS, inline=1, fontsize=clabelsize)
plt.pcolor(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data, vmin=np.nanmin(data), vmax=np.nanmax(data), shading='auto')
plt.colorbar()
plt.tight_layout()
plt.xlabel('$x$ [mm]')
plt.ylabel('$y$ [mm]')


plt.figure(22)
# fig1 = plt.figure(figsize = (5, 15))
plt.clf()
plt.subplot(311)
data = stray.Bstray[:,:,0]
#data=np.transpose(data2)

CS = plt.contour(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data , cmap=plt.get_cmap('winter'))
plt.clabel(CS, inline=1, fontsize=clabelsize)
plt.pcolor(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data, vmin=np.nanmin(data), vmax=np.nanmax(data), shading='auto')
plt.colorbar()
plt.tight_layout()
#plt.xlabel('$x$ [$\mu$m]')
plt.ylabel('$y$ [mm]')
plt.title('$B_\mathrm{stray}$ [T]')

plt.subplot(312)
data = stray.Bstray[:,:,1]
#data=np.transpose(data2)

CS = plt.contour(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data , cmap=plt.get_cmap('winter'))
plt.clabel(CS, inline=1, fontsize=clabelsize)
plt.pcolor(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data, vmin=np.nanmin(data), vmax=np.nanmax(data), shading='auto')
plt.colorbar()
plt.tight_layout()
#plt.xlabel('$x$ [$\mu$m]')
plt.ylabel('$y$ [mm]')

plt.subplot(313)
data = stray.Bstray[:,:,2]
#data=np.transpose(data2)

CS = plt.contour(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data , cmap=plt.get_cmap('winter'))
plt.clabel(CS, inline=1, fontsize=clabelsize)
plt.pcolor(stray.tc[stray.nzro_ids[1]], stray.tc[stray.nzro_ids[0]], data, vmin=np.nanmin(data), vmax=np.nanmax(data), shading='auto')
plt.colorbar()
plt.tight_layout()
plt.xlabel('$x$ [mm]')
plt.ylabel('$y$ [mm]')

