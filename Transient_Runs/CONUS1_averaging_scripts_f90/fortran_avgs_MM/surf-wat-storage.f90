  program daily_average
  implicit none
  real*8  dx2, dy2, dz2
! input variables
  real*8  press(3342,1888,5)

! output variables - daily avg
  real*8  surf_wat(3342,1888)

! output variables - daily avg
  real*8  surf_watm(3342,1888)

! output variables - daily avg
  real*8  surf_waty(3342,1888)
  real*8 dz(5)

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

nz = 5


! set running counter for PF file number
counter = 1
dayofyear = 1

! clear out yearly avgs
surf_waty = 0.0d0

do month = 1, 12

! clear out monthly avgs
surf_watm = 0.0d0

! loop over month
do day = 1, days(month)
! zero out daily avg

!clear out daily avgs
surf_wat= 0.0d0

CALL CPU_TIME(t1)
! loop over day
do hour = 1, 24
!print*, 'call read', t1
pname = '../run_outputs/pressure/CONUS.2003.out.press'
write(filenum,'(i5.5)') counter
fname=trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.pfb'
call pfb_read(press,fname,nx,ny,nz)
!CALL CPU_TIME(t2)
!print*, fname, t1

! can I re-write these as implied loops?
do j = 1, ny
do i = 1, nx
surf_wat(i,j) = surf_wat(i,j) + max(press(i,j,5),0.0d0)/ 24.0d0        !avg
end do !i 
end do !j



counter = counter + 1


!print*, 'read file:',(t2-t1)
!print*, 'looping:',(t3-t2)

end do ! hr
!  write daily averages
pname = 'surf_wat.daily'
write(filenum,'(i3.3)') dayofyear 
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) surf_wat 
close(10)

dayofyear = dayofyear + 1
! compute monthly averages
surf_watm= surf_watm + surf_wat / float(days(month))      !avg


CALL CPU_TIME(t3)
print*, counter-1, dayofyear-1 , day, monthname(month), t3-t1

end do !day
! write monthly averages
pname = 'surf_watm.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) surf_watm
close(10)

! compute yearly averages
surf_waty = surf_waty + surf_waty*( float(days(month)) / 365.0d0 )   !avg

end do !mo

! write annual avg
fname = 'surf_wat.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) surf_waty
close(10)


  end

