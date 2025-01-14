#!/bin/python3
import os
import base64
import json
from cryptography.fernet import Fernet
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

console = Console()

class PasswordManager:
    def __init__(self, db_file='passwords.json', key_file='key.key'):
        self.db_file = db_file
        self.key_file = key_file
        self.key = self.load_key()
        self.fernet = Fernet(self.key)
        self.data = self.load_data()

    def load_key(self):
        if not os.path.exists(self.key_file):
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
        with open(self.key_file, 'rb') as f:
            return f.read()

    def load_data(self):
        if not os.path.exists(self.db_file):
            return {}
        with open(self.db_file, 'rb') as f:
            encrypted_data = f.read()
        if not encrypted_data:
            return {}
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data)

    def save_data(self):
        encrypted_data = self.fernet.encrypt(json.dumps(self.data).encode())
        with open(self.db_file, 'wb') as f:
            f.write(encrypted_data)

    def add_password(self, site, username, password):
        self.data[site] = {'username': username, 'password': password}
        self.save_data()
        console.print(f"[green]Password for [bold]{site}[/bold] saved successfully![/green]")

    def generate_password(self, length=12):
        import string
        import random
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def view_passwords(self):
        if not self.data:
            console.print("[yellow]No passwords stored yet.[/yellow]")
            return

        table = Table(title="Stored Passwords")
        table.add_column("Site", style="cyan")
        table.add_column("Username", style="magenta")
        table.add_column("Password", style="green")

        for site, credentials in self.data.items():
            table.add_row(site, credentials['username'], credentials['password'])

        console.print(table)

    def delete_password(self, site):
        if site in self.data:
            del self.data[site]
            self.save_data()
            console.print(f"[red]Password for [bold]{site}[/bold] deleted successfully![/red]")
        else:
            console.print(f"[yellow]No password found for [bold]{site}[/bold].[/yellow]")

    def search_password(self, site):
        credentials = self.data.get(site)
        if credentials:
            console.print(f"[cyan]Site:[/cyan] {site}\n[magenta]Username:[/magenta] {credentials['username']}\n[green]Password:[/green] {credentials['password']}")
        else:
            console.print(f"[yellow]No password found for [bold]{site}[/bold].[/yellow]")


# Main Interface
def main():
    manager = PasswordManager()

    while True:
        console.print("\n[bold blue]Password Manager[/bold blue]")
        console.print("1. Add Password")
        console.print("2. Generate Password")
        console.print("3. View All Passwords")
        console.print("4. Search Password")
        console.print("5. Delete Password")
        console.print("6. Exit")

        choice = Prompt.ask("[bold]Choose an option[/bold]", choices=["1", "2", "3", "4", "5", "6"])

        if choice == "1":
            site = Prompt.ask("Enter the site name")
            username = Prompt.ask("Enter the username")
            password = Prompt.ask("Enter the password")
            manager.add_password(site, username, password)

        elif choice == "2":
            length = int(Prompt.ask("Enter the password length", default="12"))
            password = manager.generate_password(length)
            console.print(f"[green]Generated Password:[/green] {password}")

        elif choice == "3":
            manager.view_passwords()

        elif choice == "4":
            site = Prompt.ask("Enter the site name to search")
            manager.search_password(site)

        elif choice == "5":
            site = Prompt.ask("Enter the site name to delete")
            if Confirm.ask(f"Are you sure you want to delete the password for [bold]{site}[/bold]?"):
                manager.delete_password(site)

        elif choice == "6":
            console.print("[bold green]Thank you for using Eze's password manager![/bold green]")
            break

if __name__ == "__main__":
    main()

