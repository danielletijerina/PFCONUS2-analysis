  program daily_average
  implicit none
  real*8  dx2, dy2, dz2
! input variables
  real*8  press(3342,1888,5)
  real*8  sat(3342,1888,5)
  real*8  porosity(3342,1888,5)
!  real*8  Ss(3342,1888,5)
  real*8  Sx(3342,1888,1)
  real*8  Sy(3342,1888,1)
!  real*8  mannings(3342,1888,1)

! output variables - daily avg
  real*8  flow(3342,1888)
  real*8  sm(3342,1888)
  real*8  WTd(3342,1888)
  real*8  storage(3342,1888)
  real*8  GWstor(3342,1888)
  real*8  SMstor(3342,1888)

! output variables - daily avg
  real*8  flowm(3342,1888)
  real*8  smm(3342,1888)
  real*8  WTdm(3342,1888)
  real*8  storagem(3342,1888)
  real*8  GWstorm(3342,1888)
  real*8  SMstorm(3342,1888)

! output variables - daily avg
  real*8  flowy(3342,1888)
  real*8  smy(3342,1888)
  real*8  WTdy(3342,1888)
  real*8  storagey(3342,1888)
  real*8  dz(5)
  real*8  GWstory(3342,1888)
  real*8  SMstory(3342,1888)

 real*8 ri, rj, rk1, rk2, headsum, rsum, junk,  &
         ksum, kavg,f, dx, dy, x1, y1, z1i, mannings, Ss								
  integer*4 i,j,k, nni, nnj, nnk, ix, iy, iz,			&
            ns,  rx, ry, rz,nx,ny,nz, nnx, nny, nnz,    &
			is,dummy
  integer*4 ijk, namelength, xtent,ytent,ztent, days(12)
  integer t,counter, day, month, hour, c1, dayofyear
  real t1, t2, t3
character*100 fname, dname, pname, filenum
character*3  monthname(12)

! days in water year month starts w/ Oct
!Oct
days(1)=31
monthname(1)='OCT'
!Nov
days(2)=30
monthname(2)='NOV'
!Dec
days(3)=31
monthname(3)='DEC'
!Jan
days(4)=31
monthname(4)='JAN'
!Feb
days(5)=28
monthname(5)='FEB'
!Mar
days(6)=31
monthname(6)='MAR'
!Apr
days(7)=30
monthname(7)='APR'
!May
days(8)=31
monthname(8)='MAY'
!Jun
days(9)=30
monthname(9)='JUN'
!Jul
days(10)=31
monthname(10)='JUL'
!Aug
days(11)=31
monthname(11)='AUG'
!Sep
days(12)=30
monthname(12)='SEP'

! set dz
dz(1) = 100.0d0
dz(2) = 1.0d0
dz(3) = 0.6d0
dz(4) = 0.3d0
dz(5) = 0.1d0

nx = 3342
ny = 1888
nz = 1

! set the directory for the outputs
dname = '../averages'

! Read in Static fields
fname = '../run_inputs/slopex.pfb'
call pfb_read(Sx,fname,nx,ny,nz)

fname = '../run_inputs/slopey.pfb'
call pfb_read(Sy,fname,nx,ny,nz)

nz = 5

fname = '../run_inputs/CONUS.2003.out.porosity.pfb'
call pfb_read(porosity,fname,nx,ny,nz)

mannings= 5.0e-5
Ss = 1.0e-5

! set running counter for PF file number
counter = 1
dayofyear = 1

! clear out yearly avgs
flowy = 0.0d0
smy =  0.0d0 ! avg
WTdy =  0.0d0 !accum
Storagey =  0.0d0 ! accum
GWstory = 0.0d0
SMstory = 0.0d0

do month = 1, 12

! clear out monthly avgs
flowm = 0.0d0
smm =  0.0d0 ! avg
WTdm =  0.0d0 !accum
Storagem =  0.0d0 ! accum
GWstorm = 0.0d0
SMstorm = 0.0d0

! loop over month
do day = 1, days(month)
! zero out daily avg

!clear out daily avgs
flow = 0.0d0
sm =  0.0d0 ! avg
WTd =  0.0d0 !accum
Storage =  0.0d0 ! accum
GWstor = 0.0d0
SMstor = 0.0d0

CALL CPU_TIME(t1)
! loop over day
do hour = 1, 24
!print*, 'call read', t1
pname = '../run_outputs/pressure/CONUS.2003.out.press'
write(filenum,'(i5.5)') counter
fname=trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.pfb'
call pfb_read(press,fname,nx,ny,nz)

pname = '../run_outputs/saturation/CONUS.2003.out.satur'
write(filenum,'(i5.5)') counter
fname=trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.pfb'
call pfb_read(sat,fname,nx,ny,nz)

!CALL CPU_TIME(t2)
!print*, fname, t1

! assign fluxes and states from single CLM file

sm(:,:) = sm(:,:) + sat(:,:,5)*porosity(:,:,5) / 24.0d0      !avg
WTd(:,:) = WTd(:,:) + (52.0d0 - press(:,:,1))/ 24.0d0        !avg

! can I re-write these as implied loops?
do j = 1, ny
do i = 1, nx

do k = 1, 1
GWstor(i,j) = GWstor(i,j) + 1000.d0*1000.d0*dz(k)*    &
               (press(i,j,k)*Ss*Sat(i,j,k) +     &
               Sat(i,j,k)*porosity(i,j,k))/24.0d0
end do !k - groundwater storage

do k = 2, 5
SMstor(i,j) = SMstor(i,j) + 1000.d0*1000.d0*dz(k)*    &
               (press(i,j,k)*Ss*Sat(i,j,k) +     &
               Sat(i,j,k)*porosity(i,j,k))/24.0d0
end do !k - soil storage

do k = 1, 5
storage(i,j) = storage(i,j) + 1000.d0*1000.d0*dz(k)*    &
               (press(i,j,k)*Ss*Sat(i,j,k) +     &
               Sat(i,j,k)*porosity(i,j,k))/24.0d0
end do !k - total storage

flow(i,j) =  flow(i,j) +         &
1000.d0*((max(press(i,j,5),0.0d0))**(5.0/3.0))* &
sqrt(max(abs(Sx(i,j,1)),abs(Sy(i,j,1))))/mannings      !accum

end do !i 
end do !j



counter = counter + 1


!print*, 'read file:',(t2-t1)
!print*, 'looping:',(t3-t2)

end do ! hr
!  write daily averages
pname = 'WTd.daily'
write(filenum,'(i3.3)') dayofyear 
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) WTd 
close(10)

pname = 'SM.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) sm
close(10)

pname = 'flow.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) flow
close(10)

pname = 'storage.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) storage
close(10)

pname = 'GWstor.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) GWstor
close(10)

pname = 'SMstor.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SMstor
close(10)

dayofyear = dayofyear + 1
! compute monthly averages
storagem = storagem + storage / float(days(month))      !avg
flowm = flowm + flow ! accum 
WTdm = WTdm + WTd / float(days(month))  !avg
smm = smm + sm / float(days(month))        !avg
GWstorm = GWstorm + GWstor / float(days(month))  !avg
SMstorm = SMstorm + SMstor / float(days(month))  !avg

CALL CPU_TIME(t3)
print*, counter-1, dayofyear-1 , day, monthname(month), t3-t1

end do !day
! write monthly averages
pname = 'WTd.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) WTdm
close(10)

pname = 'storage.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) storagem
close(10)

pname = 'flow.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) flowm 
close(10)

pname = 'SM.monthly'
write(filenum,'(i2.2)') month 
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) smm 
close(10)

pname = 'GWstor.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) GWstorm
close(10)

pname = 'SMstor.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SMstorm
close(10)


! compute yearly averages
storagey = storagey + storagem*( float(days(month)) / 365.0d0 )   !avg
flowy = flowy + flowm ! accum 
WTdy = WTdy + WTdm*(float(days(month)) / 365.0d0)  !avg
smy = smy + smm *(float(days(month)) / 365.0d0)       !avg
GWstory = GWstory + GWstorm*( float(days(month)) / 365.0d0 )  !avg
SMstory = SMstory + SMstorm*( float(days(month)) / 365.0d0 )  !avg

end do !mo

! write annual avg
fname = 'flow.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) flowy
close(10)

fname = 'SM.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) smy
close(10)

fname = 'storage.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) storagey 
close(10)

fname = 'WTd.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) WTdy 
close(10)

fname = 'GWstor.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) GWstory
close(10)

fname = 'SMstor.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SMstory
close(10)


  end

