export INSTALL_DIR=/opt/oqs-vpn
export START_DIR=$PWD
export KEM_ALG="kyber768"
export SIGNATURE_ALG="dilithium3"


dnf install -y libtool cmake ninja-build make openssl libssl* pkg-config libnl3* libcap-ng* lzo* pam-devel git openssl openssl-devel perl pip
pip install PyQt6


cd /opt
echo "================================================================================================================="
echo "Retreiving Libraries (liboqs, openssl, oqs-provider, openvpn)..."
git clone --depth 1 --branch main https://github.com/open-quantum-safe/liboqs
git clone --depth 1 --branch master https://github.com/openssl/openssl.git
git clone --depth 1 --branch main https://github.com/open-quantum-safe/oqs-provider.git
git clone https://github.com/OpenVPN/openvpn.git

## Building liboqs
echo "================================================================================================================="
echo "Building liboqs..."
cd /opt/liboqs
mkdir build
cd build
cmake -G"Ninja" .. -DOQS_DIST_BUILD=ON -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR}
ninja install

## Building OpenSSL
echo "================================================================================================================="
echo "Building OpenSSL..."
cd /opt/openssl
LDFLAGS="-Wl,-rpath -Wl,${INSTALL_DIR}/lib64" ./config shared --prefix=${INSTALL_DIR}
make -j 4
make install_sw install_ssldirs;
export OPENSSL=/opt/oqs-vpn/bin/openssl

## Building OQS-Provider
echo "================================================================================================================="
echo "Building OQS-Provider..."
cd /opt/oqs-provider
ln -s ../openssl .
cmake -DOPENSSL_ROOT_DIR=${INSTALL_DIR} -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=${INSTALL_DIR} -S . -B _build
cmake --build _build
cp _build/lib/oqsprovider.so ${INSTALL_DIR}/lib64/ossl-modules
cp $START_DIR/openssl.cnf /opt/oqs-vpn/ssl

## Building OpenVPN
echo "================================================================================================================="
echo "Building OpenVPN..."
cd /opt/openvpn
libtoolize --force
aclocal
autoheader
automake --force-missing --add-missing
autoconf
CFLAGS="-I${INSTALL_DIR}/include -Wl,-rpath=${INSTALL_DIR}/lib64 -L${INSTALL_DIR}/lib64" ./configure --prefix=${INSTALL_DIR} --disable-lz4
make -j 4
make check
make install
