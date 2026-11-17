# Source1 is not in the repository. ext-rpm.sh makes it on the runner while it
# builds the SRPM, with `cargo vendor --locked` against Cargo.lock, so COPR
# builds offline from the SRPM.

# %%cargo_build runs cargo with RUSTC_BOOTSTRAP=1. The build script of the
# vendored rustix 0.37 then finds nightly features available and turns on
# rustc_attrs, whose attributes current rustc no longer has, and the build
# fails. Allowing no unstable features makes such probes fail, so crates take
# their stable code paths.
%global build_rustflags %{build_rustflags} -Zallow-features=

# Fedora's own package of this program (retired after Fedora 38) and Debian
# both call it i3status-rs, after the crate and the binary.
Name:           i3status-rs
Version:        0.32.1
Release:        1%{?dist}
Summary:        Feature-rich and resource-friendly replacement for i3status
# i3status-rs is GPL-3.0-only (Cargo.toml, LICENSE); the blank line in the
# summary is the unpublished xtask workspace member. The rest covers the
# vendored crates: update it from the %%{cargo_license_summary} output in the
# build log whenever Cargo.lock changes.
License:        GPL-3.0-only AND Apache-2.0 AND BSD-3-Clause AND ISC AND MIT AND MPL-2.0 AND MirOS AND (Apache-2.0 OR MIT) AND (0BSD OR MIT OR Apache-2.0) AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND (CC0-1.0 OR Artistic-2.0) AND (MIT OR Apache-2.0 OR Zlib) AND (Unlicense OR MIT)
URL:            https://github.com/greshake/i3status-rust
Source0:        https://github.com/regolith-linux/i3status-rs_debian/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.xz

BuildRequires:  cargo-rpm-macros >= 24
BuildRequires:  pkgconfig(libpulse)
# The vendored openssl-sys 0.9.92 aborts on OpenSSL 4 ("only compatible with
# OpenSSL … 3.0.0"), which Fedora 45 and later ship as openssl-devel. Their
# openssl3-devel provides openssl-devel 3.5 and installs in the same place, so
# this resolves to openssl-devel on Fedora 43 and 44 and to openssl3-devel
# later. The binary then needs libssl.so.3 (openssl-libs or openssl3-libs).
BuildRequires:  openssl-devel < 1:4
BuildRequires:  lm_sensors-devel
# No libdbus: the D-Bus blocks use zbus, which is pure Rust (debian/control's
# libdbus-1 dependencies are left over).

%description
i3status-rs generates the status line for the i3 and sway bars: blocks of
system information such as time, battery, volume, network and load, with icons
and themes. This build also carries the bar configuration of the Regolith
desktop.

%prep
%autosetup -a1
%cargo_prep -v vendor

%build
%cargo_build
%{cargo_license_summary}
%{cargo_license} > LICENSE.dependencies
%{cargo_vendor_manifest}

%install
# The crate has a library target (src/lib.rs), so %%cargo_install would also
# install its sources under %%{_datadir}/cargo/registry. Install the binary.
install -Dpm 0755 target/rpm/i3status-rs %{buildroot}%{_bindir}/i3status-rs
# As debian/install: Regolith's bar configuration, and the icon sets and
# themes the program looks for in /usr/share/i3status-rust.
install -Dpm 0644 config.toml %{buildroot}%{_sysconfdir}/regolith/i3status-rust/config.toml
install -d %{buildroot}%{_datadir}/i3status-rust
cp -pr files/* %{buildroot}%{_datadir}/i3status-rust/

%check
%cargo_test

%files
%license LICENSE LICENSE.dependencies cargo-vendor.txt
%doc README.md NEWS.md
%{_bindir}/i3status-rs
%dir %{_sysconfdir}/regolith
%dir %{_sysconfdir}/regolith/i3status-rust
%config(noreplace) %{_sysconfdir}/regolith/i3status-rust/config.toml
%{_datadir}/i3status-rust/

%changelog
* Tue Nov 17 2026 Regolith Fedora Port <port@regolith.invalid> - 0.32.1-1
- Initial package
