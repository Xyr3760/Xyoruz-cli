import click
import sys
import os
from .auth import request_otp, verify_otp, load_token, save_token, delete_token
from .api import api_request

def clear_screen():
    """Membersihkan layar terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause(message="Tekan Enter untuk melanjutkan..."):
    """Menunggu user menekan Enter"""
    click.echo(message)
    input()

@click.group()
def cli():
    """myXL CLI - Monitoring dan pembelian paket XL"""
    pass

@cli.command()
@click.option("--phone", prompt="Nomor XL (contoh: 628123456789)", help="Nomor telepon XL")
def login(phone):
    """Login dengan mengirim OTP ke nomor XL"""
    click.echo(f"Mengirim OTP ke {phone}...")
    try:
        ref_id, device_id = request_otp(phone)
        click.echo("OTP terkirim. Silakan cek SMS.")
        otp = click.prompt("Masukkan OTP", type=str)
        data = verify_otp(phone, otp, ref_id, device_id)
        save_token({
            "accessToken": data.get("accessToken"),
            "refreshToken": data.get("refreshToken"),
            "msisdn": data.get("msisdn", phone),
            "deviceId": device_id
        })
        click.echo(click.style("Login berhasil!", fg="green"))
    except Exception as e:
        click.echo(click.style(f"Gagal login: {e}", fg="red"), err=True)

@cli.command()
def logout():
    """Hapus token login"""
    delete_token()
    click.echo(click.style("Logout berhasil.", fg="green"))

@cli.command()
def pulsa():
    """Cek sisa pulsa"""
    try:
        data = api_request("GET", "/account/v1/balance")
        balance = data.get("data", {}).get("balance", data)
        click.echo(click.style(f"Sisa pulsa: {balance}", fg="cyan"))
    except Exception as e:
        click.echo(click.style(f"Gagal mengambil pulsa: {e}", fg="red"), err=True)

@cli.command()
def kuota():
    """Cek sisa kuota internet"""
    try:
        data = api_request("GET", "/package-core/v1/quota")
        quotas = data.get("data", [])
        if not quotas:
            click.echo("Tidak ada data kuota.")
            return
        click.echo(click.style("Sisa Kuota:", fg="yellow"))
        for q in quotas:
            name = q.get("name", "Kuota")
            remaining = q.get("remaining", "0")
            unit = q.get("unit", "")
            click.echo(f"  {name}: {remaining} {unit}")
    except Exception as e:
        click.echo(click.style(f"Gagal mengambil kuota: {e}", fg="red"), err=True)

@cli.command()
def packages():
    """Lihat daftar paket data yang tersedia"""
    try:
        data = api_request("GET", "/package-core/v1/packages")
        packages = data.get("data", [])
        if not packages:
            click.echo("Tidak ada paket tersedia.")
            return
        click.echo(click.style("Daftar Paket:", fg="yellow"))
        for p in packages:
            pid = p.get("id", "?")
            name = p.get("name", "Paket")
            price = p.get("price", "0")
            click.echo(f"  {pid}: {name} - Rp{price}")
    except Exception as e:
        click.echo(click.style(f"Gagal mengambil daftar paket: {e}", fg="red"), err=True)

@cli.command()
@click.argument("package_id")
def buy(package_id):
    """Beli paket data berdasarkan ID paket"""
    try:
        payload = {"packageId": package_id}
        data = api_request("POST", "/package-core/v1/purchase", data=payload)
        click.echo(click.style("Pembelian berhasil!", fg="green"))
        click.echo(data)
    except Exception as e:
        click.echo(click.style(f"Gagal melakukan pembelian: {e}", fg="red"), err=True)

@cli.command()
def menu():
    """Tampilkan menu interaktif (otomatis login jika belum)"""
    # Cek apakah sudah login
    token = load_token()
    if not token:
        click.echo(click.style("Anda belum login. Silakan login terlebih dahulu.", fg="yellow"))
        phone = click.prompt("Nomor XL (contoh: 628123456789)")
        try:
            ref_id, device_id = request_otp(phone)
            click.echo("OTP terkirim. Silakan cek SMS.")
            otp = click.prompt("Masukkan OTP", type=str)
            data = verify_otp(phone, otp, ref_id, device_id)
            save_token({
                "accessToken": data.get("accessToken"),
                "refreshToken": data.get("refreshToken"),
                "msisdn": data.get("msisdn", phone),
                "deviceId": device_id
            })
            click.echo(click.style("Login berhasil!", fg="green"))
            token = load_token()  # reload token
        except Exception as e:
            click.echo(click.style(f"Gagal login: {e}", fg="red"), err=True)
            return

    while True:
        clear_screen()
        # Tampilkan header dengan status
        click.echo(click.style("=" * 50, fg="blue"))
        click.echo(click.style("         myXL CLI - Menu Utama", fg="green", bold=True))
        click.echo(click.style("=" * 50, fg="blue"))

        # Ambil status terbaru (nomor dan pulsa)
        msisdn = token.get("msisdn", "Unknown")
        pulsa_info = "N/A"
        try:
            data_pulsa = api_request("GET", "/account/v1/balance")
            pulsa_info = data_pulsa.get("data", {}).get("balance", data_pulsa)
        except Exception as e:
            pulsa_info = f"Error: {str(e)[:20]}"

        click.echo(f"Nomor: {msisdn}  |  Pulsa: {pulsa_info}")
        click.echo("")
        click.echo("Pilih menu:")
        click.echo("  1. Login (ganti akun)")
        click.echo("  2. Cek Pulsa (refresh)")
        click.echo("  3. Cek Kuota")
        click.echo("  4. Lihat Daftar Paket")
        click.echo("  5. Beli Paket")
        click.echo("  6. Logout")
        click.echo("  0. Keluar")
        click.echo("")

        try:
            choice = int(click.prompt("Masukkan pilihan", type=str))
        except ValueError:
            choice = -1

        if choice == 1:
            # Login ulang (ganti akun)
            delete_token()
            phone = click.prompt("Nomor XL (contoh: 628123456789)")
            try:
                ref_id, device_id = request_otp(phone)
                click.echo("OTP terkirim. Silakan cek SMS.")
                otp = click.prompt("Masukkan OTP", type=str)
                data = verify_otp(phone, otp, ref_id, device_id)
                save_token({
                    "accessToken": data.get("accessToken"),
                    "refreshToken": data.get("refreshToken"),
                    "msisdn": data.get("msisdn", phone),
                    "deviceId": device_id
                })
                click.echo(click.style("Login berhasil!", fg="green"))
                token = load_token()
            except Exception as e:
                click.echo(click.style(f"Gagal login: {e}", fg="red"), err=True)
            pause()

        elif choice == 2:
            try:
                data = api_request("GET", "/account/v1/balance")
                balance = data.get("data", {}).get("balance", data)
                click.echo(click.style(f"Sisa pulsa: {balance}", fg="cyan"))
            except Exception as e:
                click.echo(click.style(f"Gagal mengambil pulsa: {e}", fg="red"), err=True)
            pause()

        elif choice == 3:
            try:
                data = api_request("GET", "/package-core/v1/quota")
                quotas = data.get("data", [])
                if not quotas:
                    click.echo("Tidak ada data kuota.")
                else:
                    click.echo(click.style("Sisa Kuota:", fg="yellow"))
                    for q in quotas:
                        name = q.get("name", "Kuota")
                        remaining = q.get("remaining", "0")
                        unit = q.get("unit", "")
                        click.echo(f"  {name}: {remaining} {unit}")
            except Exception as e:
                click.echo(click.style(f"Gagal mengambil kuota: {e}", fg="red"), err=True)
            pause()

        elif choice == 4:
            try:
                data = api_request("GET", "/package-core/v1/packages")
                packages = data.get("data", [])
                if not packages:
                    click.echo("Tidak ada paket tersedia.")
                else:
                    click.echo(click.style("Daftar Paket:", fg="yellow"))
                    for p in packages:
                        pid = p.get("id", "?")
                        name = p.get("name", "Paket")
                        price = p.get("price", "0")
                        click.echo(f"  {pid}: {name} - Rp{price}")
            except Exception as e:
                click.echo(click.style(f"Gagal mengambil daftar paket: {e}", fg="red"), err=True)
            pause()

        elif choice == 5:
            package_id = click.prompt("Masukkan ID Paket")
            try:
                payload = {"packageId": package_id}
                data = api_request("POST", "/package-core/v1/purchase", data=payload)
                click.echo(click.style("Pembelian berhasil!", fg="green"))
                click.echo(data)
            except Exception as e:
                click.echo(click.style(f"Gagal melakukan pembelian: {e}", fg="red"), err=True)
            pause()

        elif choice == 6:
            delete_token()
            click.echo(click.style("Logout berhasil.", fg="green"))
            token = None
            click.echo("Anda telah logout. Silakan jalankan 'myxl menu' lagi untuk login kembali.")
            pause()
            break

        elif choice == 0:
            click.echo("Terima kasih telah menggunakan myXL CLI. Sampai jumpa!")
            break
        else:
            click.echo(click.style("Pilihan tidak valid. Silakan coba lagi.", fg="red"))
            pause()

if __name__ == "__main__":
    cli()
