
program read_rst

implicit none

integer :: yr,mo,da,hr,mn,ss        ! Time variables
integer :: vclass,nc,nr,nch


open(40,file='./clm.rst.00000.0',form='unformatted')
! change to your dir

read(40) yr,mo,da,hr,mn,ss,vclass,nc,nr,nch  !Time, veg class, no. tiles
write(*,*) yr,mo,da,hr,mn,ss,vclass,nc,nr,nch

close(40)

end program read_rst