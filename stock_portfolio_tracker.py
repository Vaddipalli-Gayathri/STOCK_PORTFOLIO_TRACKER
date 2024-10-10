import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import requests
import pygame
from PIL import Image, ImageTk

# Initialize Pygame for sound
pygame.mixer.init()
pygame.mixer.music.load("C:/Users/dell/Desktop/project/sound.wav")  # Correct sound file path
pygame.mixer.music.play(-1)  # Loop the sound indefinitely

# Stock class to store stock data
class Stock:
    def __init__(self, symbol, shares, purchase_price):
        self.symbol = symbol
        self.shares = shares
        self.purchase_price = purchase_price

    @property
    def total_investment(self):
        return self.shares * self.purchase_price

    @property
    def current_value(self):
        return self.shares * self.get_current_price()

    @property
    def profit_loss(self):
        return self.current_value - self.total_investment

    def get_current_price(self):
        # Replace YOUR_API_KEY with your actual Alpha Vantage API key
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={self.symbol}&apikey=YOUR_API_KEY'
        response = requests.get(url)
        data = response.json()
        try:
            return float(data['Global Quote']['05. price'])
        except (KeyError, ValueError):
            return 0.0  # Return 0.0 if there's an error retrieving the price

# Application class for the stock portfolio tracker
class StockPortfolioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Portfolio Tracker")
        self.root.geometry("800x600")  # Set window size

        # Load background image
        self.bg_image = Image.open("C:/Users/dell/Desktop/project/Stock-portfolio.jpg")
        self.bg_image = self.bg_image.resize((800, 600), Image.LANCZOS)  # Use Image.LANCZOS instead of Image.ANTIALIAS
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        # Background Label
        bg_label = tk.Label(root, image=self.bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Create frames to manage layout and place them on top of the background
        input_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
        input_frame.place(relx=0.5, rely=0.1, anchor='n')

        portfolio_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
        portfolio_frame.place(relx=0.5, rely=0.4, anchor='n')

        summary_frame = tk.Frame(root, bg="#ffffff", padx=20, pady=20)
        summary_frame.place(relx=0.5, rely=0.85, anchor='n')

        # Input fields
        tk.Label(input_frame, text="Stock Symbol:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.symbol_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.symbol_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(input_frame, text="Number of Shares:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.shares_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.shares_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(input_frame, text="Purchase Price:", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10)
        self.purchase_price_entry = tk.Entry(input_frame, font=("Arial", 12))
        self.purchase_price_entry.grid(row=2, column=1, padx=10, pady=10)

        # Buttons for actions
        tk.Button(input_frame, text="Add Stock", command=self.add_stock, font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10)
        tk.Button(input_frame, text="Remove Stock", command=self.remove_stock, font=("Arial", 12)).grid(row=3, column=1, padx=10, pady=10)
        tk.Button(input_frame, text="Display Portfolio", command=self.display_portfolio, font=("Arial", 12)).grid(row=3, column=2, padx=10, pady=10)

        # Treeview for displaying the portfolio
        self.tree = ttk.Treeview(portfolio_frame, columns=("Symbol", "Shares", "Purchase Price", "Current Price", "Total Investment", "Current Value", "Profit/Loss"), show="headings")

        # Centering the column headings and setting headings
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col, anchor='center')
            self.tree.column(col, anchor='center', width=100)  # Center column contents

        # Pack the Treeview in the center
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Total Investment and Profit/Loss Display
        self.total_investment_label = tk.Label(summary_frame, text="Total Investment: $0.00", font=("Arial", 12), bg="white")
        self.total_investment_label.pack(side=tk.LEFT, padx=20, pady=20)

        self.total_profit_loss_label = tk.Label(summary_frame, text="Total Profit/Loss: $0.00", font=("Arial", 12), bg="white")
        self.total_profit_loss_label.pack(side=tk.RIGHT, padx=20, pady=20)

        self.stocks = []  # List to hold stock objects

    def add_stock(self):
        symbol = self.symbol_entry.get()
        shares = self.shares_entry.get()
        purchase_price = self.purchase_price_entry.get()

        if not symbol or not shares or not purchase_price:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            shares = int(shares)
            purchase_price = float(purchase_price)
        except ValueError:
            messagebox.showerror("Error", "Shares must be an integer and Purchase Price must be a float")
            return

        stock = Stock(symbol, shares, purchase_price)
        self.stocks.append(stock)
        messagebox.showinfo("Success", f"Stock {symbol} added successfully")
        self.update_totals()

    def remove_stock(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "Please select a stock to remove")
            return
        stock_symbol = self.tree.item(selected_item, 'values')[0]
        self.stocks = [stock for stock in self.stocks if stock.symbol != stock_symbol]
        self.tree.delete(selected_item)
        messagebox.showinfo("Success", f"Stock {stock_symbol} removed successfully")
        self.update_totals()

    def display_portfolio(self):
        # Clear the existing portfolio display
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Add each stock to the Treeview
        for stock in self.stocks:
            self.tree.insert('', 'end', values=(
                stock.symbol, stock.shares, stock.purchase_price,
                stock.get_current_price(), stock.total_investment,
                stock.current_value, stock.profit_loss
            ))

    def update_totals(self):
        total_investment = sum(stock.total_investment for stock in self.stocks)
        total_profit_loss = sum(stock.profit_loss for stock in self.stocks)

        self.total_investment_label.config(text=f"Total Investment: ${total_investment:.2f}")
        self.total_profit_loss_label.config(text=f"Total Profit/Loss: ${total_profit_loss:.2f}")

# Running the application
if __name__ == "__main__":
    root = tk.Tk()
    app = StockPortfolioApp(root)
    root.mainloop()