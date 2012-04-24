IF EXIST python-2.7.2.msi (
		MOVE python-2.7.2.msi python-2.7.2.msi.bak
		)
IF EXIST pygame-1.9.2a0.win32-py2.7.msi (
		MOVE pygame-1.9.2a0.win32-py2.7.msi pygame-1.9.2a0.win32-py2.7.msi.bak
		)
echo "Begin download file 1..."
wget http://python.org/ftp/python/2.7.2/python-2.7.2.msi
echo "Begin download file 2..."
wget http://pygame.org/ftp/pygame-1.9.2a0.win32-py2.7.msi

echo "Don't close me!"
python-2.7.2.msi
echo "Don't close me!"
pygame-1.9.2a0.win32-py2.7.msi
