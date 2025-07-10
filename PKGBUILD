pkgname=post-install-linux
pkgver=1.0
pkgrel=1
pkgdesc="Scripts de pós-instalação para Arch, Debian e Fedora"
arch=('any')
license=('MIT')
depends=('bash' 'python')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('3fd6b5f668c3bdc3ff68ce6aec6d67539d3cca1a9e52a0b08cf41ef6ba508a07')
url="https://github.com/seuusuario/post-install-linux"

package() {
  install -d "$pkgdir/usr/share/$pkgname"
  cp -a "$srcdir/$pkgname/." "$pkgdir/usr/share/$pkgname/"

  install -d "$pkgdir/usr/bin"
  echo "#!/bin/bash" > "$pkgdir/usr/bin/$pkgname"
  echo "exec /usr/share/$pkgname/main.sh \"\$@\"" >> "$pkgdir/usr/bin/$pkgname"
  chmod +x "$pkgdir/usr/bin/$pkgname"
}
