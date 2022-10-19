  program daily_average
  implicit none
  real*8  dx2, dy2, dz2
! input variables
  real*8  press(3342,1888,5)
  real*8  sat(3342,1888,5)
  real*8  CLM(3342,1888,17)

! output variables
  real*8  flow(3342,1888)
  real*8  sm(3342,1888)
  real*8  WTd(3342,1888)
  real*8  Storage(3342,1888)

!  CLM variables - daily avg
  real*8  SWE(3342,1888)         !CLM out layer 11 [mm]
  real*8  Tsoil(3342,1888)       !CLM out layer 14 [K] @5cm
  real*8  qflx_trans(3342,1888)  !CLM out layer 9 [mm/s]
  real*8  LH(3342,1888)          !CLM out layer 1 [W/m^2]
  real*8  SH(3342,1888)          !CLM out layer 3 [W/m^2]
  real*8  Tgrnd(3342,1888)       !CLM out layer 12 [K] skin temp
  real*8  qflx_grnd(3342,1888)   !CLM out layer 6 [mm/s]

!  CLM variables- monthly avg
  real*8  SWEm(3342,1888)         !CLM out layer 11 [mm]
  real*8  Tsoilm(3342,1888)       !CLM out layer 14 [K] @5cm
  real*8  qflx_transm(3342,1888)  !CLM out layer 9 [mm/s]
  real*8  LHm(3342,1888)          !CLM out layer 1 [W/m^2]
  real*8  SHm(3342,1888)          !CLM out layer 3 [W/m^2]
  real*8  Tgrndm(3342,1888)       !CLM out layer 12 [K] skin temp
  real*8  qflx_grndm(3342,1888)   !CLM out layer 6 [mm/s]

!  CLM variables - yearly avg
  real*8  SWEy(3342,1888)         !CLM out layer 11 [mm]
  real*8  Tsoily(3342,1888)       !CLM out layer 14 [K] @5cm
  real*8  qflx_transy(3342,1888)  !CLM out layer 9 [mm/s]
  real*8  LHy(3342,1888)          !CLM out layer 1 [W/m^2]
  real*8  SHy(3342,1888)          !CLM out layer 3 [W/m^2]
  real*8  Tgrndy(3342,1888)       !CLM out layer 12 [K] skin temp
  real*8  qflx_grndy(3342,1888)   !CLM out layer 6 [mm/s]

 real*8 ri, rj, rk1, rk2, headsum, rsum, junk,  &
         ksum, kavg,f, dx, dy, dz, x1, y1, z1								
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

nx = 3342
ny = 1888
nz = 17

! set output directory
dname='../averages'

! set running counter for PF file number
counter = 1
dayofyear = 1

! clear out yearly avgs
SWEy = 0.0d0
Tgrndy =  0.0d0 ! avg
qflx_grndy =  0.0d0 !accum
qflx_transy =  0.0d0 ! accum
Tsoily = 0.0d0 !avg
LHy = 0.0d0 !avg
SHy = 0.0d0 !avg

do month = 1, 12

! clear out monthly avgs
SWEm = 0.0d0
Tgrndm =  0.0d0 ! avg
qflx_grndm =  0.0d0 !accum
qflx_transm =  0.0d0 ! accum
Tsoilm = 0.0d0 !avg
LHm = 0.0d0 !avg
SHm = 0.0d0 !avg

! loop over month
do day = 1, days(month)
! zero out daily avg

!clear out daily avgs
SWE = 0.0d0
Tgrnd = 0.0d0
qflx_grnd = 0.0d0
qflx_trans = 0.0d0
Tsoil = 0.0d0
LH = 0.0d0
SH = 0.0d0

CALL CPU_TIME(t1)
! loop over day
do hour = 1, 24
!print*, 'call read', t1
pname = '../run_outputs/clm_out/CONUS.2003.out.clm_output'
write(filenum,'(i5.5)') counter
fname=trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.C.pfb'
call pfb_read(CLM,fname,nx,ny,nz)
!CALL CPU_TIME(t2)
!print*, fname, t1

! assign fluxes and states from single CLM file

SWE(:,:) = SWE(:,:) + CLM(:,:,11) / 24.0d0      !avg
Tgrnd(:,:) = Tgrnd(:,:) + CLM(:,:,12) / 24.0d0      !avg
! should I multiply these two fluxes by one hour (3600 s)?
qflx_grnd(:,:) = qflx_grnd(:,:) + CLM(:,:,6)     !accum
qflx_trans(:,:) = qflx_trans(:,:) + CLM(:,:,9)   !accum
Tsoil(:,:) = Tsoil(:,:) + CLM(:,:,14) / 24.0d0      !avg
LH(:,:) = LH(:,:) + CLM(:,:,1)/ 24.0d0      !avg
SH(:,:) = SH(:,:) + CLM(:,:,3)/ 24.0d0      !avg


counter = counter + 1


!print*, 'read file:',(t2-t1)
!print*, 'looping:',(t3-t2)

end do ! hr
!  write daily averages
pname = 'SWE.daily'
write(filenum,'(i3.3)') dayofyear 
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SWE
close(10)

pname = 'Tgrnd.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) Tgrnd
close(10)

pname = 'qflx_grnd.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) qflx_grnd 
close(10)

pname = 'qflx_trans.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) qflx_trans
close(10)

pname = 'Tsoil.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) Tsoil
close(10)

pname = 'LH.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) LH
close(10)

pname = 'SH.daily'
write(filenum,'(i3.3)') dayofyear
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SH
close(10)

dayofyear = dayofyear + 1
! compute monthly averages
SWEm = SWEm + SWE / float(days(month))      !avg
Tgrndm = Tgrndm + Tgrnd / float(days(month))   ! avg
qflx_grndm = qflx_grndm + qflx_grnd   ! accum
qflx_transm = qflx_transm + qflx_trans ! accum
Tsoilm = Tsoilm + Tsoil / float(days(month))  !avg
LHm = LHm + LH / float(days(month))        !avg
SHm = SHm + SH / float(days(month))        !avg


CALL CPU_TIME(t3)
print*, counter-1, dayofyear-1 , day, monthname(month), t3-t1

end do !day
! write monthly averages
pname = 'SWE.month'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SWEm
close(10)

pname = 'Tgrnd.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) Tgrndm
close(10)

pname = 'qflx_grnd.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) qflx_grndm 
close(10)

pname = 'qflx_trans.monthly'
write(filenum,'(i2.2)') month 
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) qflx_transm
close(10)

pname = 'Tsoil.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) Tsoilm
close(10)

pname = 'LH.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) LHm
close(10)

pname = 'SH.monthly'
write(filenum,'(i2.2)') month
fname=trim(adjustl(dname))//'/'//trim(adjustl(pname))//'.'//trim(adjustl(filenum))//'.bin'
open (10,file=trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SHm
close(10)


! compute yearly averages
SWEy = SWEy + SWEm*(float(days(month)) / 365.d0)      !avg
Tgrndy = Tgrndy +Tgrndm*(float(days(month)) / 365.d0)   ! avg
qflx_grndy = qflx_grndy + qflx_grndm   ! accum
qflx_transy = qflx_transy + qflx_transm ! accum
Tsoily = Tsoily + Tsoilm *(float(days(month))/ 365.d0)  !avg
LHy = LHy + LHm*(float(days(month)) / 365.d0)        !avg
SHy = SHy + SHm *(float(days(month))/ 365.d0) !avg
end do !mo

! write annual avg
fname = 'SWE.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SWEy
close(10)

fname = 'Tgrnd.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) Tgrndy
close(10)

fname = 'qflx_grnd.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) qflx_grndy
close(10)

fname = 'qflx_trans.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) qflx_transy
close(10)

fname = 'Tsoil.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) Tsoily
close(10)

fname = 'LH.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) LHy
close(10)

fname = 'SH.yearly.bin'
open (10,file=trim(adjustl(dname))//'/'//trim(adjustl(fname)),form='unformatted',access='stream')
write(10) nx, ny, 1
write(10) SHy
close(10)

  end

