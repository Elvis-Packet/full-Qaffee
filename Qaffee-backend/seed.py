from datetime import datetime, timezone, timedelta
from app import create_app, db
from app.models import (
    User, UserRole, Category, MenuItem, Branch, Promotion, Reward, 
    Order, OrderItem, DeliveryAddress, Review, Payment, Notification,
    SupportTicket, Feedback, LoyaltyTransaction, RewardClaim, 
    Referral, StoreLocation, FAQ, ReferralCode, ReferralUse,
    OrderStatus, TicketStatus, TicketPriority, NotificationType, LoyaltyPoints
)

def seed_data():
    app = create_app()
    with app.app_context():
        # Clear existing data (uncomment only for development)
        # db.drop_all()
        # db.create_all()
        
        # ========== USERS ==========
        users_data = [
            {
                'email': 'admin@qaffee.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': UserRole.ADMIN,
                'phone': '1234567890',
                'reward_points': 1000,
                'password': 'admin123'
            },
            {
                'email': 'staff@qaffee.com',
                'first_name': 'Staff',
                'last_name': 'Member',
                'role': UserRole.STAFF,
                'phone': '1234567891',
                'reward_points': 500,
                'password': 'staff123'
            },
            {
                'email': 'customer@qaffee.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'role': UserRole.CUSTOMER,
                'phone': '1234567892',
                'reward_points': 200,
                'referral_code': 'JOHNDOE123',
                'password': 'customer123'
            },
            {
                'email': 'customer2@qaffee.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'role': UserRole.CUSTOMER,
                'phone': '1234567893',
                'reward_points': 150,
                'password': 'customer123'
            }
        ]

        users = {}
        for user_data in users_data:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    email=user_data['email'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    is_active=True,
                    phone=user_data['phone'],
                    reward_points=user_data['reward_points']
                )
                if 'referral_code' in user_data:
                    user.referral_code = user_data['referral_code']
                user.set_password(user_data['password'])
                db.session.add(user)
            users[user_data['email']] = user
        
        db.session.commit()

        # ========== CATEGORIES (UPDATED WITH BETTER IMAGES) ==========
        categories_data = [
            {
                'name': 'Middle Eastern',
                'description': 'Authentic Middle Eastern flavors',
                'image_url': 'https://images.unsplash.com/photo-1551504734-5ee1c4a1479b?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80'
            },
            {
                'name': 'Burgers & Sandwiches',
                'description': 'Juicy burgers and hearty sandwiches',
                'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1598&q=80'
            },
            {
                'name': 'Pasta & Grills',
                'description': 'Italian pastas and grilled specialties',
                'image_url': 'https://images.unsplash.com/photo-1621996659490-327aff0fa9e1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1470&q=80'
            },
            {
                'name': 'Seafood & Biryani',
                'description': 'Fresh seafood and aromatic biryanis',
                'image_url': 'https://images.unsplash.com/photo-1631515243349-e0cb75fb8d3a?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1588&q=80'
            },
            {
                'name': 'Desserts & Beverages',
                'description': 'Sweet treats and refreshing drinks',
                'image_url': 'https://images.unsplash.com/photo-1571115177098-24ec42ed204d?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=1587&q=80'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category = Category.query.filter_by(name=cat_data['name']).first()
            if not category:
                category = Category(**cat_data)
                db.session.add(category)
            categories[cat_data['name']] = category
        
        db.session.commit()

        # ========== MENU ITEMS (UPDATED WITH BETTER IMAGES) ==========
        menu_items_data = [
            # Middle Eastern - Updated with all items from the menu
            {
                'name': 'Kebabs',
                'description': 'Grilled skewers of marinated meat with spices',
                'price': 750.0,
                'image_url': 'https://thesageapron.com/wp-content/uploads/2023/07/Lamb-Shish-Kebab-9.jpg',
                'category': categories['Middle Eastern'],
                'is_available': True,
                'ingredients': 'Lamb or chicken, onions, bell peppers, Middle Eastern spices'
            },
            {
                'name': 'Shawarma',
                'description': 'Slow-roasted marinated meat with garlic sauce',
                'price': 650.0,
                'image_url': 'https://i.pinimg.com/736x/ab/9a/81/ab9a813697d74c4c4edb40fc223048b0.jpg',
                'category': categories['Middle Eastern'],
                'is_available': True,
                'ingredients': 'Chicken or beef, garlic sauce, pickles, tomatoes, pita bread'
            },
            {
                'name': 'Falafel',
                'description': 'Crispy chickpea fritters with tahini sauce',
                'price': 550.0,
                'image_url': 'https://i.pinimg.com/736x/a9/d8/c4/a9d8c42532032507aa67d44c794c3a90.jpg',
                'category': categories['Middle Eastern'],
                'is_available': True,
                'ingredients': 'Chickpeas, herbs, spices, tahini sauce, pita bread'
            },
            {
                'name': 'Hummus',
                'description': 'Creamy chickpea dip with olive oil and pita',
                'price': 450.0,
                'image_url': 'https://i.pinimg.com/736x/34/91/d1/3491d149a865324058b441a677440bbc.jpg',
                'category': categories['Middle Eastern'],
                'is_available': True,
                'ingredients': 'Chickpeas, tahini, lemon juice, garlic, olive oil, pita bread'
            },
            
            # Burgers & Sandwiches
            {
                'name': 'Beef Burgers',
                'description': 'Juicy beef patty with fresh toppings',
                'price': 750.0,
                'image_url': 'https://i.pinimg.com/736x/ea/be/96/eabe96a9b405b4f11904ef480f713a2f.jpg',
                'category': categories['Burgers & Sandwiches'],
                'is_available': True,
                'ingredients': 'Beef patty, cheese, lettuce, tomato, onion, special sauce, brioche bun'
            },
            {
                'name': 'Chicken Burgers',
                'description': 'Grilled chicken breast with signature sauce',
                'price': 700.0,
                'image_url': 'https://i.pinimg.com/736x/52/7b/91/527b91e2dd095c9d29ba7d4ec98a2928.jpg',
                'category': categories['Burgers & Sandwiches'],
                'is_available': True,
                'ingredients': 'Chicken breast, lettuce, tomato, onion, signature sauce, brioche bun'
            },
            {
                'name': 'Veggie Options',
                'description': 'Plant-based burger with fresh vegetables',
                'price': 650.0,
                'image_url': 'https://i.pinimg.com/736x/7a/33/64/7a33642c2bacd45027db8d9007ab26a0.jpg',
                'category': categories['Burgers & Sandwiches'],
                'is_available': True,
                'ingredients': 'Plant-based patty, lettuce, tomato, onion, vegan mayo, whole wheat bun'
            },
            {
                'name': 'Qaffee Point Special',
                'description': 'Our signature burger with special ingredients',
                'price': 850.0,
                'image_url': 'https://i.pinimg.com/736x/28/df/09/28df09263b54af6ae8a146f7b6631da3.jpg',
                'category': categories['Burgers & Sandwiches'],
                'is_available': True,
                'ingredients': 'Beef patty, special sauce, caramelized onions, cheese, brioche bun'
            },
            
            # Pasta & Grills
            {
                'name': 'Lasagna',
                'description': 'Layered pasta with meat and cheese',
                'price': 800.0,
                'image_url': 'https://i.pinimg.com/736x/42/d6/a8/42d6a8928f8bd852dcd4f70adbfbb09a.jpg',
                'category': categories['Pasta & Grills'],
                'is_available': True,
                'ingredients': 'Pasta sheets, ground beef, ricotta cheese, tomato sauce, mozzarella'
            },
            {
                'name': 'Seafood Pasta',
                'description': 'Pasta with mixed seafood in creamy sauce',
                'price': 950.0,
                'image_url': 'https://i.pinimg.com/736x/b9/2b/d1/b92bd1b52a12a8eb2077e9bed3133097.jpg',
                'category': categories['Pasta & Grills'],
                'is_available': True,
                'ingredients': 'Pasta, shrimp, mussels, calamari, cream sauce, herbs'
            },
            {
                'name': 'Mixed Grill Platters',
                'description': 'Assortment of grilled meats and vegetables',
                'price': 1200.0,
                'image_url': 'https://i.pinimg.com/736x/d3/00/e6/d300e6a6f995a82fe9a62eb43a46abf0.jpg',
                'category': categories['Pasta & Grills'],
                'is_available': True,
                'ingredients': 'Chicken, beef, lamb, grilled vegetables, dipping sauces'
            },
            {
                'name': 'T-bone Steak',
                'description': 'Premium cut steak with sides',
                'price': 1500.0,
                'image_url': 'https://i.pinimg.com/736x/01/3b/d9/013bd95fe22a1e443ae65373339a024c.jpg',
                'category': categories['Pasta & Grills'],
                'is_available': True,
                'ingredients': 'T-bone steak, mashed potatoes, grilled vegetables, peppercorn sauce'
            },
            
            # Seafood & Biryani
            {
                'name': 'Seafood Platters',
                'description': 'Assorted fresh seafood with sides',
                'price': 1300.0,
                'image_url': 'https://imgs.search.brave.com/NDyuWYJF5WaqkUrMHWN-cCi54VvnAJodNd-jmGSgMSI/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5nZXR0eWltYWdl/cy5jb20vaWQvODU2/NTI0MzMvcGhvdG8v/ZmVhc3Qtb2YtdGhl/LXNldmVuLWZpc2hl/cy1zZWFmb29kLXBs/YXR0ZXIuanBnP3M9/NjEyeDYxMiZ3PTAm/az0yMCZjPTA1ci10/V1NNVkVjVXBtb2lV/S2xmZnpkRjhOV0w3/cU16ZkRJc3R1eWNJ/dXM9',
                'category': categories['Seafood & Biryani'],
                'is_available': True,
                'ingredients': 'Shrimp, fish, calamari, mussels, lemon butter sauce, vegetables'
            },
            {
                'name': 'Lobster Specials',
                'description': 'Fresh lobster prepared to perfection',
                'price': 1800.0,
                'image_url': 'https://i.pinimg.com/736x/29/ae/ba/29aeba9eebbde76f42e7ee0989859ac2.jpg',
                'category': categories['Seafood & Biryani'],
                'is_available': True,
                'ingredients': 'Whole lobster, butter sauce, lemon, herbs, side of vegetables'
            },
            {
                'name': 'Chicken Biryani',
                'description': 'Fragrant rice with chicken and spices',
                'price': 800.0,
                'image_url': 'https://i.pinimg.com/736x/30/30/69/303069c67eaf155e09297748239c6fb3.jpg',
                'category': categories['Seafood & Biryani'],
                'is_available': True,
                'ingredients': 'Basmati rice, chicken, biryani spices, yogurt, fried onions'
            },
            {
                'name': 'Vegetable Biryani',
                'description': 'Aromatic rice with mixed vegetables',
                'price': 700.0,
                'image_url': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMTEhUTExMVFhUXGSIaGBgYGR4bIBoYHRgYHRoeHR0YHyggGB4lHxcYITEiJSorLi4uGB8zODMtNygtLisBCgoKDg0OGxAQGzAlICUyLS03Ly4tKy0wMy0vLS0tLS0wLS0tLy0vLS0vLS0tLS0vKy0tLy0tLS8tLS0tLS0tLf/AABEIAKgBLAMBIgACEQEDEQH/xAAcAAACAgMBAQAAAAAAAAAAAAAFBgMEAAIHAQj/xABEEAABAwIEBAMFBwIFAwEJAAABAgMRACEEBRIxBkFRYRMicTKBkaGxBxQjQlLB8GLRFRYz4fFDcqKCNFNUY3ODkpPC/8QAGQEAAwEBAQAAAAAAAAAAAAAAAgMEAQAF/8QAMREAAgIBAwIEBAUEAwAAAAAAAQIAEQMSITEEQRMiUfBhgZGhFDJCsdFxweHxBRVS/9oADAMBAAIRAxEAPwBLHEzafZRWrnGi/wAqQKUAg1sGuppuuZUYHuLnzziqLvEDx/OaHaE9a91oFZqM6pMvMnDupR99Ql5Z61794T0rPvB2ArrnVNYUalZ1Dej2T8H4/E3S0UI/W55BHvufhRscL4DDf+2YwurG7bIn4kSfmKydEcsFR3ojgeGcS9/psOK76SB8TApqHFmFw9sJgUA/rduf3+tDMw44xztvG0Do2An/AHrZ0sYf7N8QBLy2WR/WoTU3+Xcsa/1seFkbhoT9JpMxWKWsytSlHqok/WoZrJ1R3++5M37LL7x72HzIrP8AN+ER/pZc0O6zP0FLGUZUt8kJISBuVUbY4JdUSEvNWE3JH7GkP1WJG0s28oTo8zprVdpaV9oDw/08Ph0eiJqL/PuOUQElsE2AS2Kt5XwRqYeLik6wU+GUKkRPmmQLmnnB8L4ZKWlJQEuNgArAuYFieUnmaU3W46tN5v4VwacVOdZrxPmbKy266pC7GNKee2wr3NMwzhjT4y30aklQsk+UbnygwLiukeI86q7IKZgq8pIA7b0eecDuHlAClA6bmNjCgbbWoMXVu4J0/wCYT9MFI3nCcRxLmLatK33kqiYUADB25V63xbjv/iXP/H+1OnE3BDj+LQ8kEhwArQog6SAIAULabUQd4ZbxbBaSnStoQjQANKwRqCiYsb27CnfigGCkcxRwmiYrZLm+ZP6/DeKtCStUpTsPdvUuH4mxZ3W2r1bH7V0PKuF2cL4ga1DxGwhQJk/m819pmh2M4T/BX5Ut6UgAb3GxkbmtPVKrURY/acuAsLuoqf465+dnDL/9EVuc9aUkocwaNJ30Kj9qA4p0oUULspNjVY4gVcNBFiSnUDGVheAQ0toNvspUZJHmgxFrmpOG+H8oU4kOYwlH6VHSSeUzypSfxMgUMxCqFgO00X3n0zlPCGVAAssML7zr+pNL32k/ZkziWS5hQll1AnSBCFgcoHsnuPhXBMPmDjZltxaD/Soj6Uw5f9peYtW8cuJ6Lv8AOlQqhn7O+JTgXyX8OYjQSIkQeVbfadxlh8YtHhDTp57Gqo47wj404vCaSd1tH/g1B/lDAYsE4LGgLOzbtj6cjRXM0wPl3FLzVgoqR0JpvwnEbOIAC16T0NqBOfZ+4y2VP6pG2nzJPwFUGeGnVJlCFk+kfWtsjedQO06G2gR5IIqJ10jdMUt5VwtmQIKDoHcz8qd8syDFkfjqQfQR9azxVm+C3aCw+a21HrTCvhfoYNUcRw08NjNb4iwTiYQK8T1qirXyNXcdhlIsoEGhZxRFopgiiJzIIVUgYVUnjV4X6RKZgwp5mpsPl5WoJSCpR2AEk+4U18NcEvPp8Z8jDYcXK12JHYHb1NOLHE+XZcjRgWA89zdc29eqvSw70QEEtFvKPsyc0h3FrGHa3v7R/YfOr5zXA4Ly4LDpcWP+s5f4fwUEzziDE4tWp9wq6J2Sn0SLChK1xRUBM3MKZxxFicRZx1RT+keVPwFAlmtlOVEqTsD8KEtCCwjkeCDiiViUjl1JqbF5AnVCXICjaRYDlJHe1WsmwbyGVOKbUlEyF9hv86ttvpWytIjX7QHUDePrXktmy+OSDtO0tfEVMzyp1lehQk8im4M1tkWUKxD6Gbo1GCopNqZH0qeW1q8ilpABUCNWgn6gi9H8IwfvEKB8NSPKEm6TAm49PnTT1TXorcxoxkrqgrHZd9ya8MJhZHnUTZR1EBQntFqqcM4xZfKFSCm994sP3FHs5zrCgpQ+2t3TYaiJt1kitnVYJ1pWLY1NLBCHAbmCBB3Pbaktj1qSaM9rD1LY0CUR2hDKnUeI9h1eWUagehkERTZkGch1s6k3R5SYA1dxG09K49neKe8XxGm1rSUgEpSTe/SjfDvEDja0Hw1JJOhTa0qRIPO6YMTQYQ2KjW0i6vKcuSj8P2nUMwYBGtAgm2pJgx36ilfC4xGHWWysq1LtBlKCfaM2Krm/S9WeMM2CWkhudSzp1AwkEe1Mc+1JuEaUW1KkkgkTO1ulb1OXel+sPpsXkJc7Rwx2NdZeKdgbggbgm3w51dy/M0NKKAgBPtyDzN1b7mZpedzFacEVvFPiMkFKidxqA5dQaXhxakEAG89bX6npUIGV913lA8Ir5qnVGMcYu6n3i3uI3FSuI8VGkLSsf0q/vSdluf60zpuY81ojrP7Vcy5to4jUl9KQQAUCPMom1uU01crHysPuf7xbYkUarqB/tM4b/CS8gQ4kQf60+u0ikbL8k8ZJ0uhKhyVsegttXYM/yFeJR4Hj6W9QUSBexuBeB60jZnwgvBPJCHCtLl0qCN4IkKvvcG29WJkyLj22r5ybw0ZvUmI2cYB7DLCHk6SRI6EdQedDlOV0fOMr++qYQ4taVAEazeBNxBvUOUfZzLWLLslafKxFgTAIXvzmIPSq06pGG5k79O6njac5JrQ0Tz3Jl4VwtrIVpiVJmJiYnqOlVcbgXGtIdQpBUNSQoRI600OGFiKKkGjKhrU1Ia1Ka24MP5JxpjcNZDpWj9DnmHzuK6Jw99qOGXCcS14Kv1C6f7j31xxIrcCt55mgkcT6mwGJadSFNrStJ2KTNXA2K+Xsnzh/DK1MOKQeg2PqNjXVuFPtTQ5DeLAbVtrHsn1/TQnH6Qxk9Z0yKwVA3igoBSSFJOxF6wumlHbmMG88xWAQsQoClrF8L+YxEUxlZ61rNaHI4nHGDzPmvBcPLcUEJlSlWAFOX+FYLKEhzEgYjFkShndKOhV/f4UUzPHt5S14LRSvGrT517hsHp36D31y/GrWtZWslSlGSomSTVRko3lviHijE4xUvOHT+VtNkp6W5++omsUAAT1g1TSzUrjXkpZYzajDhWW12Ssj1FV83y1bUE3SdlDr07UKy9ZKgB7Wwp/w2BVpSwqXSsSUpG3vqDPmy4WDarHp3nKpgDhnh84lLi9QCWrqB9PkKZsmygISh7QhfnSlSCrYlQE9Fcrd63wOWoZC0JDjQUfOk7q7X5VebLYhDYITq1GTNhG9Iz5myeZeJ6fS0q0e/wAPZknFTD63V4ZpHkVpKSBYAiTPcGjWX5PhwlCVoQl1CdIcIgKtBnrVB7PgpzVcyISB251tmWZqKEqhMAxM2Bm23LapDm0uTHjAWA7bS/j8IVCElrUlNki/bflQRrOCyUgqBi9xHqBVXGKdLyn2VpSsjzp0ygq/UAdqmwp1hSsSEKWD5dI8qRGwTA1fPpWZG1tzx/WMXEEXfeFPDD61oxeDR7MhwwZB2AIuFCqLXCjOHVqbWVNKklpY1eYDywReL85NqIIS460paXDqQbgjduLn+dDUD2chtIKtp0mPSi8fKDXY/WKKqAaPHMvJXiAAEFLaNE3A3Av6cqEYhh55DhClLUgBUEblRtA6xJrVLj2NWoylCUwCCeXpBnn2po+86UpRqvA1L7AXPyo1N/mJ+sSMtnyL9on8IY5Lri8HiEgym02Nu/UTIIoJh1ELW1MLQpSFGN4JE/KafnuHMGgjE3Q4nzeIXFbaSDYnTt2rmWOzZP3p1aLpWrVexmAD8xPvp2XGDjpeZV0lZsuk8H9404bCKPhpUpGgkBZP6CRNjbYVfxf2b4TxU+G2pLVy755AAEgJ1TBM7bQKW8DnCFQFgyDYiZHwpzyXM/ItBcVB2VuQTyINyJqTDkGK1O1xvVf8XoFoPlOd4jFXKUkAAaRpAAJSSAbWMgCDUeU4glxsKXADiIMbDUOYnaJ+NSY7KSysh5aU2kkE3BmPLymx3tNNHBfD65+8KbEEamtZg3FjAHPlPWqVFdp4y4WO7cQyM5QlxALmsFR1GCmBy339e1MbryMQ1oBA5pVvB5e6kXBZ0XHSlbKNaTCkKTaZiNuW1Es04wwzD6GoS2EiHAkbKMERp/Tz9Y5UpWamC/MV/eek+KyNvnczEJStOtKwooMShu6Z31HcC1EfuriWQW3QYMqJ6dPSiasybLSVtjUhYNwdM8vWfnS45gSlSkNuqRuQ2qSnsJJv7qzMoXe/v9J2Jidjt73kuIyBp1LZe0gJcDpAvrPccrxSXxXw09iMxQlalaXZ0uASlLYFgOQIrpmVYfW2UqASpSSkxf51dawAabsdUcj9RVHTu+kEcVJs6JZ9bnzRmWF8J5xomdCimfQ71vg8red/02lr9BXecbw7hXnfGUy2tSbkxue/Wlritv7ukOYVLiCknWdgE9hVLdVQFCD0/SDI+ljXvvOV47K3mY8VtSJ2kfvVWui4XiRC21NYhIII5if+K0yXgkLUh6PwiryiRB/tTMfUhtiN53U9A+DckV6znoNbUc45wiWcTpCNEiY/fvQDXVKNqFyJhRjTwpxjiMGoBJ1tc2yfp0NdpyDiBnGN62VXHtIO4PpXzildXMrzZ3DOB1lRSofAjoRzFEwDczFJHE+lEntW80ucHcWN49qR5XU+2j9x1FHdVTsumUK2qfNT+LUtZWtRUpRlRO5J3NSioGmQN6nKqoJuTT0AVGu9bhVTMZY46hxSYCUASTYEk7CsnTonBPB7SsK0taEh0yrVF9J2HrFTM4ZLa/wlBx2TCFRMdQOUVTwHFLzSEJKUylMWuNrV5isIoq+8NAK1wdSdx1nmCL15+bIjDZbMYAy7wvmObIdGhxtSFp/UBP8Auk0qvYtCXBpFiQVIBjUgHa200baQt5B8cwoEFox5k9j19KD4dps4hS1bAx6x/vNTMFQE3PSwWw4jI4ylaDiEo8NIACE91GJttf6VA5jW2Wy24NYWICQmTHbuT06Chz+LWtxQJPhpICQB5QJ37E6ue89rEczLshQBKPERpIEyqALdNzfa1SOPMAPdytBt5oPczdGtLSWg3znnblFSPvr3T5Y5dag4jzbEMOFKvDUeRIkgdDBrXLXQo61FZLiYAPUSbDkKM4uDBBpeIcyHGuNuJVGpKjpcPJI7+lrd6o8RYQh8ISU6ASpN7meQHa4mquDxIQFtqXp1G0kQD69xFS8T45KENnyl0phHMgkCVe6nqhZd/dybILevWUMJjVhxwJJ0TGq8CAJ9TJIp4XlzTrSV+LoAHmO4V20z1pSwGCaDbYWtQK5CYGxmATO/+9RZlgi2NK3SIN0weexHIgpg8jeKSUAY2spoNQBr5Rgz/FeJhiCUpMTsdo2FrTH0rnD2Glta0qMpMqHKBVrO8/KU+E0qUEQSdzYR8DPrFV8kdW60pCElStrCZB3mOVUoj6dRmrpQ0plrh/Np0tkJi5Bi+rlTYwoyXBIVuRyMbzSbhMr+6pW49YgeUR3/AOKvYDOHQlHiIWkuAaVxqm28DrS82MPekWJVj6jzC9iYdzDJUYjEodQqVFGsoWfL5SkJ0dTvY28vemTKHcQtfhqSAke2Vg2E/lI3mDFD8swLBSgvBK4MpK0iyp5TzkDamR7FpQJkJKtv7xQ4E10zkjT9/wDcg6pwrFUFg8fCAc1Tl+EdWtzFaXSSqNOtQmDy23FjFc/YaU4pZOynFLSqAlSgVWJ3O0WnnTxnuZEpUHnELH5YRCvqZPpFKvC2DUValqASSQmbD0HQCRTs+YBTo2ndKhJ828eMuxK8Oyha9LuG3UNIQtsn2lCPKpMyeXOj7hab80BUmU7See/MUBzJlxGH0y2pJlMBV/MIHz+oohk7AS1hvHELCNOgnmBc2O9qBMmtN6BFcwMqUdQ7k8Qpl+apdJCkaTyPvomViKHsNtkxpWmD7j09RRFlQuEqkixHTpVOLG/6iD8ZFldb8oqUHwE3TueQqjiGEuJIcRItqHLeQasv4+ASe8eoGw61QxuIX4CSBBMar7Ty+NJyKtFlPEZj1EhfWKfHWXpEqSgJkkzbzCK94aGjDpDi5acX4ei/lIGorEchaireWtvyHCVEC0qNj/zQTNHzhNDT5BbS2st6fzlW9+u3oKHp3sWff+IzOpHluc243xOrFuJDniBB0pX1A6TQHVTwnJULR4w0GTcKG9pN6hTlLDiQEIFxEzce7nVo6pFABEz/AK7I6l0IMUULqXVW2ZYPwnCgGQOZqFJqoNe4nnspBowhk+bOYZ5LzRhSTtyUOYPY19BZBnLOMYQ+lUahChOyhuDXzfVnDY5xsQhakgmYBi9v7Ci2PMyyOJZ1VotdaqVUS9qydUsYNxBWAtRSnqPlT7w0guJLQcHhpGxElQPOlJeVNFtCFjw3InxEypKwevQimrIcrDY1pWIi0A3PxqTqn0jcx+Bbvaaf4etvEEOo1Nc4m47EbUaLXgI0tSUm87269q9xmIBEkwfzDn6itDmCXWtKBGvymOQi/paoUyqRXErbGbDGQoXIPmM7yeVLqcXpcWORM+/nRFLnh6kIjodV5Hr1/vW2GyrDPJILmi9yBMWtb151ugPG48oWyN57hsd5SLEK3921EctzVxLbiUQQ2hTgHMBN1Gff86W8dlrjJCUEuXgmOXI9hvTlkzSmMOlxMFTgAVIjQTcgwTPr2FqWMFGydhHZcq6bHeLWCwSloW6oys383IE7350NTinUut640uAxe4AO/abfGm555Y8RTukApMFN5pSxmPGrUN9OnblvatwnUTYgkky6AEpLu4SAIk8zHL60Hfxxde8RWq0ACfZEdqsqzsDDEIUAtS5g8hP0gfOqbrKikOpHtbmCClXOexmqUQqtGDrDPZjDl8v+E2kiQrebQTJ+AE+6r/HgS5iLPNNpCUtyon2hJKvL0mPURSdhcetuSEQd5Eb8zVXEv6nUqBKiVpIneZ2iuVDqqG1DzAy3nmQugeOhSHmifbbNh0kHbpzpn4T8VOGQGFIUpVz5bJ7KUeYjYUbyDDtJ8XUkjxAEhAEIO4mPZ5/CtsFhnvvoZQmW0DVFoPKDz2UDJtTNYZdpIXN7wNxtgVrCLEgCXCB5bfS9a5Rh2kIQFJWPKdJuYV1IOw7etMvFOXqabISqSs3QLkJ5if5FDcCw1ASoq1E7nlYxbpNQZ8zIKqW9OFdbviVcnafW+AUKUAoSpRG0bi/LoO1e8U5YnE4sKeeUhpA0ANkT17/m3tsKNZbgjrMaikb23T0Ta5i8TS9jeHVM/jHFMeCtZCSsqCpuQDYgmAqbjY0WF8hQldt/feBmGPxKJ7Q1iMBl3lgrJgAC94EchM1OxhWERpY1xuLmx3JE0tYtaQ4lDLodVv5DcGNrG/Wr+CzvQs/lUDCgbi288xS2LdxXynKO6m/nCGG4hS++RpCUpX5QYsE2v74V76JYnE6n1NuDzSPDNtjEEHl399B3cWziFkAQFJglIvaTPUkapkURczAF4J5JSnzKIlRiUkdOfIXBpTnY794a5FZ9IWiB7MYMZi9KCSTI50KOYyoEJlR3Ooj5japvHXrA8MBK5UdREDraOp270Dewi0uOXOgGQQkgQb2+MUw5srbL2995C2JK3l1eZnEAoKHEKTEKGlXm7gG++8R76rpYxLTeohlyTGhBKSZ7bVr/AIjBQAokp5mBAi4neO1KWfvvYdwYhpStLp1+X2QZ8wnYGQTHenkDJxzJGIQ+YTouXZMVocWr8NxxEdQmRvaocv4caThww68XgkyA6lJ0/wDbaQPfSlhuNMQ7cLgRGkcjG9VsTj39YdS55imFjnANzEWnf41qZEQ6ahDqVynSTvC2ccIYDVP3pbZmNJgpk7DaRSFjsudZUoQSkGAoc/3pucQpTyEKMKUAXEwJGqNPtWB8wNU8fkD7rBcWSXCsBKQqEgCZUaqJXvK8GZ8RtTEXHOyDqF+9DkmjXEuSu4YpS8RqUJABmR6mggFVYq07SfqcpyPZEkFbg1GK3FHEVcLZVlbmJcDTekL0kjUYmOQ70OdSpKi2oQoHSQeRmL0wcN5UvEYsBtzwigawuJggiBEjcn4TThxFgkERimEazBUtIjzWGpKtyNv3pTZdJnBbgnJWEhtIVKxpjzC3SjWDcSdaFDTCQEHaD/IoGp1KlqbSqChIUhKTY32Py+NFsLljzrK1tuJWtBu0JB7b2PWvN6hWLWZbiKgVKeMxP5XJChzFv9iKt4l4eEF/nIgcvpUuWsN45pTDiSnEMiUnZUybHtNiD1BqirUFNqcb1IFigEyI3Bi6T/alIgA35jc7krS8yo0kKVpJuYv6mCfd+9F2so0FbbigQdtJgxFjRX71h2glTeGTrV+VUlQ5/mmrmMwLDxBxTQQrdEqEnboepiD0qkaFFk3JcSMgquYLfDi0WDalJEXsopHMxY0OzVxbTBS+ANYBbKefO5mByselGcVlQZIUwUzsrWSbWumNjvQTi0OOYZAgK0qJlInSPTpyoUZHaNy2EPpFROaOJ2WY3KbEH3bCi2S4cOI8QJGsk3VsByI+lKLi+/b3e6iWGUlOHV7ZWo+RIJgEmxIHW/rNVnCABJundh5e0nzjDtJ1rRqUkGCqDAM9Tbe1F8hXOF1KgCTfsOZ+FUXXVDLClQIUFEQoRErnnUmd41TmHQG0hIcuoD9Ow9xtQuupa+MepOqZlIZxGHWFDS4JCSm5tsP5aoMKU4bEJJhSYkAi8jnq5USyvh1QUlxpaBpErSRplJ3EjmOU/Kq2fNNuFtBXocJgExEHrJFjEetYSNYVeDCFlSWl3KMwfxOKSAoeU69BXCdCVAxYbkGKdc3xamHPHZDmt2ygm6QEJAEyIRvyMnvFIWUZcphJWJUtJlOkRO3M9RNeu8dLSS0ppYClgqClbItsI3kE1xxm6WCWB3nQ8PmJXh9DoSVrOkEcjKYBJvN9xSq7iCla2nZbUkqS2sdBtMyJiN7GjLb3gNuA3VGpI3lQEgfIUn53mD2LfUhbPhKcukSZ53kgcv3pAXUvmjsdhvL3h7CZpiW2nUrJWSk+GtEC8W1DcD/t+VqkyZSHcO5hHQQ06CUKidK/aO+x1X7kHrSrl2V4llZSjEhIBgoUJAM3Gk7e6mvFZW64wkIcIclMkWhU3IA+hrThCEaJhcmw0o8HcO/d8R4jqdakqIbA2Bi6zJ7wBfn2qt/jmrHvKaYWC5YoVycTZSjG3/NT8R5w40+hpu+m7hO5mwHrufeKoZgshxLwvB80W3Am/P8A4rsjsDpbf+ZqY9Q1Dn0hrHp8MhQOnbsAbztcbT8auZZmOr8NXmSuBsJkXkdPX30OxLmuYuCkEG8yCrlNolMx+raKFs4wocKk29TeZvzvsKhOM8ieSMrB77zoeNUVOS2rShCCJN/NIsQeorMzc8VPhpjWUSLwfnv76B4nNVNToBbSVA2XE6jclRBkSZvyEVTY4paBSdKkG6SpN7iRtMimJhJ3Hznv+GdpfxXCjoQnU5AnzwJIB5K+RmvMTwo792U0hYcQVakhtISZiPMVK80VexWudQJ/EIXZU64G9uUeuw2odluJW7ilIQl2FeZelzSECYJAjrcXohQbYe/pEHCSNRraIruRvNr0KGlYE6VWM8oir2MYxGGCFuLbUFCwCvMJFwbXt6inDFZAllKnHcQpT6lSm8nTI3BBJMc/hSdisqce1ONkHSo/hqsrT1M/SmE2aeqkv4XEdxCDTc+ZC4K9nDcieqZv0pv4ZU2UAAlTjY06Xd5B3gVx5OJKFXnUDyMU5cOYlzxUukqU2o+YixTbe257V2YEAVKkxgg7wxxdk68SxCxC9eokgA6QDYEi1yNq49iGNC1J6Gu+OsuFtfiYhOi90gE6Y7ix+NcRz5DQxCwypSkdVRM89htT+hLAUZJ1AF2IOAr2KkSK90VfcnowzhszLLwUDAiCBzHQ0df4uU6giBA3QsXHfuKUcyw62nFNuApcQqFA7gj+TNbYfGazDhSkDmaScIO/eEr1GPhLFNKdWt5CUpu3I3BPOeUWohkmWP4bE604nUSbFPmC0A/nBt/DBpVfxqSpKW0wgHc2k9ep99X8uxhsBIveOk3+VIzo36e8owFT+adjy7MG1JV5UhUXUIvHftVHNX23wFMLbkxJncA843ttSlhn0aktpHlcVcT5QknnPLsKl4qdKHlpOn2U6YGnykb/AB1X7VASR5CL/iV4sYLauIYawzeoFRlwAxe3uobj8epZuAFD9Uq0n5bUEweaadQbCdcRP/H8+FEXcbqShRIS7HmlO5/9O4rmUny8Q6ptR3hLC5sVpShYbK+swD19JHShmPxLjry2ZShKEmEJEAki0ncxM8qtfefZQoadcDUERE877CqOd4zD4NHhswVke1vHqZ3vVC4+SDFM4viB/wDLIPQDmtRj4DnRDC5eG0kNPBd7xFiPpy+FU8tC8SEIWViFSFco7dTc/CiycQHHSw2dCUGJtqUeZGrejYMyaTzBUqrWOIFznELLZSRMkEjqByFW22vBGkNtltaLwIJJ784//rtVzNXE4dK1rJX5oEgDkOneaBffnHQFaJSgR5QSBJHftQ4y4WhDbQxsw1mDwbaSkNqUYiJEzzN9/T0qrj+Gw4yFkFs8tR1qNvzHYegqThxxxSvYKxHtLMRvck0zsYkFN4Uk2tcWsT8f2osNJzFZSTxE1/A460vBQ/pIBHqNMVBk3DRxUqU4QAfOvtF0gbT35TRjP8tRqTDriXXSEpTJAUfZAiL3I71ZxL4w62ME2fKCnxFDe5/cyfhVIahZ7QNN7DkyLN8WsohClCD5FKNylA8yjEc7fOt8M87iC1qUn2vIsJuFT2gcqJ43LWFv+J7IS3+Y2SJVJE/WoMvx7GkpYb8mqzirSoQqUjp029KRfl1DiHYNADeS5xlYWp5/QA54dpEQtJgKBO3K/wDTU2XZgGEBTjmtWoa1iITAJAgcth76ZsI6XLoRJTEHqDuL2nmKUuL8gU2XHvDWppUrJSk+QwJBA32mYpioRjsbxesM+k7QPi3UYh1T3hQTYlOoyomyrnfYQLCtcOdTUkTPlUOihb9qs8ONhy7Y8qovykbx+9XgzhUqWPEKipfmjYKSEhUQOUibm/vqd8ZYWY8ZNJ0iB2grTpnlCTsRtzG4sLHpQvUVLAVKf1cu0xHSnZWTNqQSy5JG4NwB6jag2MwaXSlC1FtSJuRYzHOdrUsqU/N9Yk9PiyvrG3qIXwynFI8jYcSTAE7HfaL7D+Gi+By5biEqISTMFJ/Le/z/AGqhwjg1h5KUFISm6zMz0jvPM9KeW8SJ9kRuLb/3rceDxVBY7R+bqShpZUThGrJUfMBGqYjoIFh2qXCZU20CW0hKjdUC6h672v8AOqLoaClLUCgKElJ3CufM1by/N21oSQqY/N1Hc04jGvIAktuRsSRBWJwrZWgk6lXMzB7i142qMZFhlBStSkkd5v3m5q/mwb8NxaWwt0DylA8w9IvaSaSXOM1AiAJFidie1eeUKnamEqU6httKqeGVqxqE4dsBKE+d0pJbPMKE/n7Ci2HwSmVKQNAhUJMTI77DryqrmvEjy8It5tegt2IEQRaO4Nzta1R4TM0t4XxipXiOJIbQoyrUd1np/OtONuoA7d4QBG5PPaH22/MVrcN/QC3851z37QcuaSA82ACTCoEah3jn35g0Swoedssr3k/CQSTsO9WsacvCAnGPeIQQdMkAe5F43NzTMGsOD7MDqAirXJnMWzVgVPmJZU8s4ZCks/lCiVGwub3vvFNvDn2euYlgPKWGwo+UKFynkfQmfhXq1fE8+6G8bM1ynD5s0jFshCn0DZVguPyOD9QO0+mxkIOZYDCPakpQcLiEWUiIhQ5FJ+oiocszV7BPeI0d/aQTZY79Fd66flj+DzPTiEpQMSgaTqHmH9KxzHRXw6UORCw1Id5g8pppydrKygSYWZgcv+agUhbdk6TqET0p3zh1zB/hqBSoRpkSCI82gjcXHwM0u5tiGnZKEaSbqN7k9J2qFcuQtTCXjCumxL+QZMCfEZdKIhKtQmVxMiCIE/WmHM8GMSx4C3B46R5Vkc4Eg9Um1/SkfLs1Vh0QZuoRa/wo81nTaxKiUrkEGY25EHrESP7VNmTL4mr7/wAx2PTpqLjeFWHSnUlshUEHkRY2oorX7JKSBMkc72tyNVeI3G3FhwCFqASrvpkT8IHuqbMHkNow6RaxKiOe3+9U1romDrKbRhzFan8O28gFa2vK4gWKk9R3G/oT0pdTh0PLLKUqKj0Ps25cvjUYxL7BDzBPhuWBMe6xv6E96jwLjqdakqShU3tcqPPaE+tauOt/fzmDIQNMjODxLb6SjWsIOyTtBhQjrvTdisv8FxGIUghTiPID152/KqCAZG1D+DcC4lLryFE6JmeStIJ5/wAmmzIsV97aKHwkupOpEdBY/wA70OXLR27feAuPv9YLw6EKA8chcXuBbfa3z3qLB4hloqWPaVfSNgdp9TUOcpbaeVLgGsCBawvIF+orbLFs3CRqKRJWocucdKQuQkWI04wBvCipCUpBAWYJjsQSPTl76sMOaZCUgCSTAgyfr60LxOMVBKCJG9T4TGu7KSFA9LEe7Y/y1Hgyqdid4rJjYC6lVeboU8nRrW40oEp0GwJg7i1pvMVvicrYeeU4Cpt9RnzXSsgCIE2iOUG2xqVpuVk7ybkWOmJuPlNau4FlJLpCyE3HmUo6h0k2ix9ao8TTse8ACztJMHjB958B5FleXrfkLcjNHf8ALeFQnQpZStKiULkgabQkpnTYGJsaqsNtlbeJVqStItPcEQR180VDjcMlS1uFwqBsUqGwO8T1oWHhr6/xOsMdtv5hlnEBAQhsiAZ8kXtz3POeW1FE54QtDUFalXIT+VIgFSpNhJA6nlMUl5ZmCS6EB4akyCCItsBJ35UHzzJMYl8uLcX4bk/iIuBYwiBdIsN7HuZosWXSu0E4QzU0YuMMxWtwIwKPFUEqS5oA/DMpiTz3Mb3B6UDy3JXXcE0GQnWl5ZJJ0wPMk7ifaSKtcJB1ttaB7OqyrCes+6PhVzMM5+6I8RYltJAIRc3Mc4HTnSjmLtVcxmjwxQPEKtcPlGGSy0soW4R4roGoixKj5jtYJ9/U0u8YZaykJbdUtZH/AFBCEmQfKq9zzgdKsYvjVRJW2n8MJ2XAv1tM+lC8RijiG9Klg21HVss789u1DkyhdkEdiwOx1PGfgvCMoYUllsIXEK3lcTpVJ9SPWmjHYpJIQk3SifST/t9K57wpmIQvRJECFJVyH5SDzH7V0PUlQCgkTtIHKm4XfRV3+8l6hArxd4wzFQSEx5dtRi5ESOo3FLDWaKKYgkbBKRz5WFNHEyWTqZecKNUKSRAIItaQeY+dQZflKFspSlwBtKp29ojqZ+NT58JyvR+kdhzLjS6m2GzNvQEeEUrIumdKlc/KsH96QOJy2cSrSy6xKbpXdSlnUdUyQQSRcHkTVni/PHSpxoqACCUgDkQbEHl60IxHEDzzaWnVhaUmUlQGodtW8VSiADb9op7Bs9/jDfCCW1NOIXCgTGk9YtPW9a8SYdhrDqIbKHQoCSVHmJFzAtJtS/l2bow61iFK7D9UfSaH5vnTj8FZ2AEDaRN46maUnTv4pP6Y1swCg94x43jJxOHQAEp8ukab6rb/ANMCkbFYlTiioxJuYqDxDXQ/s9+z5x8h/EpKWj7KCPM57j7Ke+/1r01x6Z5zPqM2+zThFWIUHnEnwQYSObiug7d666/mTDR8MoLhTY6QshJ/SNCSLCPj0gkRm2b+GU4PBgeIoaStMaWkx7KO8fm6fMhl+F8JsISdtzzJ5k9TRFgk4KW3nFMQ2FiOfI0Nw+JcYcDjaihxPMdOhGyh2NGo9PdVTHYPUJG/1paGpRkUNHjJeN8NjEDDY9tIJsCfZKuqVboV6/E1WzTgF5klzBrDrZGyhK0+ke0PnXN3ERY0f4c4yxOEICVeI2P+ms7D+lW6ffIpjKrjeIVmTiVFYQlai4SSmyj07RyrzOMMPCQ62CRzj8p/kiukMZvluaJ0ODwXzzslc+vsufOgWJ4CxeFKiyU4pg30iyxO/lJg+4+4VM2F1OodpSmdSK9YnNJXKDFhfvepVYRDi9PmQs+/tI+FHcywTyWwpQ8JIgEECTeL3maEOp/EQ4lSbRPWB8qVq+RjDv8AGEeJcHoUhI8qUtgoJEgnmPcI95qrkuaNoBQ6tSdcy7o1WiwAg6fgetT55mqtIISFJNj2kD4g0tqftfftQ4NRTcTX0zrKc7wzDIa8MaFCIFtVrzG81Fl2Zs+I2vDt2m+naOcyfpSBleYoSdamw4mNOhf5T1B/m9MWGz1EQ2gpI5W+E1JlwuO9mPQrVVGTMMsZedJmUEykdJubdjb3V4xw402lwgiQCUgSOX8tSpic5WDqKdI7KH0NFcBm6h4esFeq0JVBE2+HvpIXIpsjb+sNvy0DKWDwRB1qcCG/6hIVawF96vYfCLJC0+Ui4J2J79RVfM8cG9DCRKW3Q54axzE2k/l+O9E8PmilFRdSkKUPImdgNz8xVKY1NMeYnJlatuIZwjTYxHjhPtI0rRNif1DvYCaizBhnWkpSoAK1AFUgH9xS1hWncMVJdJUhQCtVzCSLT0Peq2PzhxCFeGQoDcKvA+pqot+mpMEJNgzM2xzrrifMEpSqbbCDv/UauKzkKBJ0xMdKB4F8hhDkawZKkmOZMAWtFU8apTxAZRA/SIHrJ5UkoxNEysBa44jzleTYV1sOLWWVxC4UClUfm83Xp2puwDaEBDbboUkDrJ+M2pCRiDZKUafIAlG8ETI6HcX9a9wOJWg6ghwAWISLzN6RlytxV/GYuLVZv5Q/xLmWlelTekjZX608iD8r0s4lCnVJ1ONobEwFGZPInYWH1r37SnpLASrUnSTHMEET3vbf9JpDw2HU66hCFEhagkSZ0km+/Ln7qdjwFzquLZtCihDTzolSUwpMkSnYxa3avWjPNW0AA/Wh2Y4FWGfcZCwoJVExE2BHpvtVgvlB0mxA/bkedG+LTxKMWexvL7uJUNJBgp59vXpTlwZxUUpGuS3fUbeUhR5TJBHSubLdNwP5ap8A8sN6RaSB6Akb/WsVSnmXmdk05PK065xAwzjWgEPDWm6F9Z5HrMDbmB6ULeQvDs4YujypUAvnB0m9t5M0FxOaIQ62hCNKdAmBMmTf1t86aMuzZ1Y8PSNpSVXHv5zSz1FmyNz6SU4yqgXtA2P4dy9xwtnW064NU6zJkk+yqU9bACkXOsmcwzxZWNXNCttaeRH0I5EU24ziFpta9SPxXEwVqBUEpBsEz0MkDrW2I1ZhgWnUpUXUKEaR5jfSoDtMK91WYmLJuN4hgQws7TmmPb0rvzE/GvMBl72JcDTCFOKPJI27k7AdzXZsp4Q/CKX4ShaSFIgFUHuDCT3k1Fi+JMFl6PAwjYUv9Dd79XHD+96owhiLYVFZWF0u8qcKfZ2xhB4+MWhbibwf9Nv4+2flUuc8bKcJbwohG3ikXV/2jp629aUMzzd/Fq/GVI5Np9hPr+s+tqaOF8o0kOLEq/KOnetfKF2E3HhvdowcMZX4Sda7uL3m8A358zzo4Xh2oelR5mvdQ61Pqj9E5KHifZFZp61KEjl8qjJjkB86ZClDGsA+tCHG4piWAe9QYhlKhtWhqi2UGAkQTCjA6xMUfyPjbGYYgJc8RA/K5e3Y+0PnQbE4YpqqRTg0Qy+s61hOP8FjE+FjWdJNiTce5Sbj3xU2N4Hw2ITqwmJAHJJhSf8A8k3HvmuOzVzL8zcZVqbUQff9RBrSqNzBtl/LG/GcH4/DyCx4rZ5tnWAPTf3RS3jsuVrKRIP6TY+8U0ZP9pr7dnAVDrv/AGP1pow3HmCxNnm21H+oCf8Ayg0B6U3aGGOq2pxOY/4cUJjWNQvFRNqI3N5rqbnDWUv3QVMqP6Vnf/tXI+FUcX9mII/AxST01pj5p/tSXw5BzH4+oSc+MadxI3FaIfUgEyZOxm4jaKa3fs2xiFEhCVp6oWCfgqKC43h3FIPnwzwCdvIVfNM0vRXIjfEDd5viM8deUFuBMxFgd4AnfcxRbE4mCFdBA9VECPkKBJSAPNKVgyAoR9axGIJJlczciNoiKTtvtMyuEW414vG+OsoCvIoeH6k2kHsT9aH4thlJUwULbcT5VGSQSOYJkEfA1QYzIJHoIA+npUWPxQJ1AmTuDe/rS1yPZBEjw5v/AFLiwq6UlIBt6elRYFxtJUUza0zv8KDYnGrbUYI2sassFKcNqAJIub73AphxuRzLkyAx0yN1I8IeRxzrPmvvPTl2qdedOB51RaUlpCtJMT5jvfYClDI8SoPAyACLk8hYz8qaG+Ig2LkRMhP6v5+9RZMdHSRcep3sQu+994RocZCkCFeZMSLwe3Og2f5CwhaMWyNBQRqQgDTY+1AFjff+mtGuJjodWYAvAHTT/eatYfiFsI/GMSkEJt5v4azH4mIiia+sNkD9oi5hhy5iHlSUrUZST7JECPfarGa4VTjaTstN7X9R+/uphzzKS6lDmHaUmRGhCZB/qgbb1tknCuOWdLjcIixUL+kTPxr1MeXxBYEgdNBoxHwj0eVRmdqOYJ5CRCog700p+zNSjqW6hvqANX9oNWzwlleHTOIeK4/UvSPgiD7q5+nbIfSGvUoq1IMJlAWW3m1BxGiDChIXykWtvW+VZPjlPoWU+G0kyqSCVD9I6CtXePstwo04VkKI/wDdoj/yO9Lua/abjHZDaUMp6nzK+dvlTF6NAAG7SduoYk1HvMuEcIpRdxK/KDITq0ADmCrciZNC8Xx7gsKnwcG2FxsGxpSPVVcrxuOceOp51bp/qNvhXjZ5Ae4VQqqo2iTbcmMOc8U4rEyHHNCD/wBNqw/9St1UPwrJPlSIHQfy9b5bly3FAJEmnzJshS1BVBV8hSsmSPx4pBw9w9ohbgvyH96aQQBUCHOQ+Nb6qnu5TXab+Ia1Kv5FehPWtgroK6dOZwahcarKymxdzTQdq1g9qysoTCE08KZnaqOJy7mgz2r2solJgMAYMcaIsRUZFZWU8GTkTKw1lZRQDJWMWtHsLUn0P7bUVwfFuKb2WD6iPmkisrKMOw7wdKntDuD+03EJ9pM+ip+o/ejDH2tEDzIVPp/Ymvayu1+onaBLbX2sYdX+oyfgD9alHHGUOe2y3ffU1/YVlZWbHtMqZ/imQr3QyPcpP0rC3kC/zN//ALVD96ysrPDU9pk0dyjIVbuJt/8APP8Aepm8BkgTpDyY/wDrf71lZW+GvpC1MO81bwWSJk+Km+/45/vWBWQpvLRPdxSvqa8rK4Yk9J3iP6z05/kiPZbaP/2yr6isP2j4BFkNC20IArKyt0KO07Ux5Mp4v7WkCzbKj8qA477U8Wv2EIR3MqNe1lZcyotY/ifGPf6mIXHRJ0j5UJUqTJlR7ma9rKy509Cjyt6VslM1lZWHaEBcuMYQmj+U5MFEBRisrKndjK0QCP2XYRDaQEJA6nr76sk1lZSY4TZE1Int868rK6cZuE9bmvR6/wA91ZWVsyf/2Q==',
                'category': categories['Seafood & Biryani'],
                'is_available': True,
                'ingredients': 'Basmati rice, mixed vegetables, biryani spices, yogurt'
            },
            
            # Desserts & Beverages
            {
                'name': 'Waffles',
                'description': 'Crispy waffles with toppings of your choice',
                'price': 500.0,
                'image_url': 'https://imgs.search.brave.com/FDmsaAscJXVeeAavXvF5KlEWsKSUk6gOva2QQKfUdBc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9wcmVw/cHlraXRjaGVuLmNv/bS93cC1jb250ZW50/L3VwbG9hZHMvMjAy/My8xMC9XYWZmbGUt/UmVjaXBlLUZlYXR1/cmUuanBn',
                'category': categories['Desserts & Beverages'],
                'is_available': True,
                'ingredients': 'Waffle batter, maple syrup, fresh fruits, whipped cream'
            },
            {
                'name': 'Brownies',
                'description': 'Rich chocolate brownies with ice cream',
                'price': 450.0,
                'image_url': 'https://i.pinimg.com/736x/a3/83/8d/a3838d3c24ed85761d721453d83084df.jpg',
                'category': categories['Desserts & Beverages'],
                'is_available': True,
                'ingredients': 'Chocolate, flour, eggs, butter, vanilla ice cream'
            },
            {
                'name': 'Smoothies',
                'description': 'Fresh fruit smoothies with yogurt',
                'price': 400.0,
                'image_url': 'https://i.pinimg.com/736x/f8/ad/65/f8ad65769817f03f9c34967f3fc0df39.jpg',
                'category': categories['Desserts & Beverages'],
                'is_available': True,
                'ingredients': 'Mixed fruits, yogurt, honey, ice'
            },
            {
                'name': 'Specialty Coffee',
                'description': 'Artisanal coffee brewed to perfection',
                'price': 350.0,
                'image_url': 'https://i.pinimg.com/736x/e4/7b/53/e47b53bcb1a2fd4c17797a19aba368da.jpg',
                'category': categories['Desserts & Beverages'],
                'is_available': True,
                'ingredients': 'Premium coffee beans, milk (optional), sugar (optional)'
            }
        ]

        menu_items = {}
        for item_data in menu_items_data:
            item = MenuItem.query.filter_by(name=item_data['name']).first()
            if not item:
                item = MenuItem(**item_data)
                db.session.add(item)
            menu_items[item_data['name']] = item
        
        db.session.commit()

        # ========== BRANCHES ==========
        branches_data = [
            {
                'name': 'Main Street Branch',
                'address': '123 Main Street, Cityville',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'contact_number': '123-456-7890',
                'is_active': True
            },
            {
                'name': 'Airport Branch',
                'address': 'Airport Terminal 1, Cityville',
                'latitude': 40.6413,
                'longitude': -73.7781,
                'contact_number': '123-555-7890',
                'is_active': True
            }
        ]

        branches = {}
        for branch_data in branches_data:
            branch = Branch.query.filter_by(name=branch_data['name']).first()
            if not branch:
                branch = Branch(**branch_data)
                db.session.add(branch)
            branches[branch_data['name']] = branch
        
        db.session.commit()

        # ========== DELIVERY ADDRESSES ==========
        delivery_addresses_data = [
            {
                'user': users['customer@qaffee.com'],
                'address_line1': '123 Customer Street',
                'city': 'Cityville',
                'state': 'State',
                'postal_code': '12345',
                'country': 'Country',
                'is_default': True,
                'label': 'Home'
            }
        ]

        for addr_data in delivery_addresses_data:
            addr = DeliveryAddress.query.filter_by(
                user_id=addr_data['user'].id,
                address_line1=addr_data['address_line1']
            ).first()
            if not addr:
                addr = DeliveryAddress(
                    user_id=addr_data['user'].id,
                    **{k: v for k, v in addr_data.items() if k != 'user'}
                )
                db.session.add(addr)
        
        db.session.commit()

        # ========== PROMOTIONS ==========
        promotions_data = [
            {
                'code': 'WELCOME10',
                'description': '10% off for new customers',
                'discount_type': 'percentage',
                'discount_value': 10.0,
                'min_purchase_amount': 0,
                'start_date': datetime.now(timezone.utc) - timedelta(days=10),
                'end_date': datetime.now(timezone.utc) + timedelta(days=30),
                'is_active': True,
                'max_uses': 100,
                'current_uses': 0
            },
            {
                'code': 'FREESHIP',
                'description': 'Free shipping on orders over KSh 2000',
                'discount_type': 'fixed_amount',
                'discount_value': 150.0,  # Average delivery fee
                'min_purchase_amount': 2000.0,
                'start_date': datetime.now(timezone.utc) - timedelta(days=5),
                'end_date': datetime.now(timezone.utc) + timedelta(days=25),
                'is_active': True,
                'max_uses': 50,
                'current_uses': 0
            }
        ]

        promotions = {}
        for promo_data in promotions_data:
            promo = Promotion.query.filter_by(code=promo_data['code']).first()
            if not promo:
                promo = Promotion(**promo_data)
                db.session.add(promo)
            promotions[promo_data['code']] = promo
        
        db.session.commit()

        # ========== REWARDS ==========
        rewards_data = [
            {
                'name': 'Free Appetizer',
                'description': 'Redeem 100 points for a free appetizer',
                'points_required': 100,
                'reward_type': 'free_item',
                'reward_value': 0.0,
                'is_active': True,
                'start_date': datetime.now(timezone.utc) - timedelta(days=30),
                'end_date': datetime.now(timezone.utc) + timedelta(days=365),
                'max_claims': 100,
                'current_claims': 0,
                'terms_conditions': 'Valid for any appetizer item only.'
            },
            {
                'name': '15% Discount',
                'description': 'Redeem 200 points for 15% off your order',
                'points_required': 200,
                'reward_type': 'discount',
                'reward_value': 15.0,
                'is_active': True,
                'start_date': datetime.now(timezone.utc) - timedelta(days=30),
                'end_date': datetime.now(timezone.utc) + timedelta(days=365),
                'max_claims': 50,
                'current_claims': 0,
                'terms_conditions': 'Valid on orders over KSh 1500.'
            }
        ]

        rewards = {}
        for reward_data in rewards_data:
            reward = Reward.query.filter_by(name=reward_data['name']).first()
            if not reward:
                reward = Reward(**reward_data)
                db.session.add(reward)
            rewards[reward_data['name']] = reward
        
        db.session.commit()

        # ========== ORDERS & ORDER ITEMS (UPDATED) ==========
        orders_data = [
            {
                'user': users['customer@qaffee.com'],
                'status': OrderStatus.COMPLETED,
                'total_amount': 1450.0,  # 2*450 + 550
                'delivery_address': DeliveryAddress.query.filter_by(
                    user_id=users['customer@qaffee.com'].id
                ).first(),
                'is_delivery': True,
                'payment_status': 'paid',
                'created_at': datetime.now(timezone.utc) - timedelta(days=2),
                'items': [
                    {
                        'menu_item': menu_items['Hummus'],
                        'quantity': 2,
                        'subtotal': 900.0
                    },
                    {
                        'menu_item': menu_items['Falafel'],
                        'quantity': 1,
                        'subtotal': 550.0
                    }
                ]
            }
        ]

        for order_data in orders_data:
            order = Order.query.filter_by(
                user_id=order_data['user'].id,
                created_at=order_data['created_at']
            ).first()
            
            if not order:
                order = Order(
                    user_id=order_data['user'].id,
                    status=order_data['status'],
                    total_amount=order_data['total_amount'],
                    delivery_address_id=order_data['delivery_address'].id,
                    is_delivery=order_data['is_delivery'],
                    payment_status=order_data['payment_status'],
                    created_at=order_data['created_at']
                )
                db.session.add(order)
                db.session.flush()  # Get the order ID
                
                for item_data in order_data['items']:
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=item_data['menu_item'].id,
                        quantity=item_data['quantity'],
                        subtotal=item_data['subtotal']
                    )
                    db.session.add(order_item)
        
        db.session.commit()

        # ========== PAYMENTS ==========
        payments_data = [
            {
                'order': Order.query.first(),
                'amount': 1450.0,
                'payment_method': 'stripe',
                'transaction_id': 'ch_123456789',
                'status': 'succeeded',
                'created_at': datetime.now(timezone.utc)
            }
        ]

        for payment_data in payments_data:
            payment = Payment.query.filter_by(
                order_id=payment_data['order'].id,
                transaction_id=payment_data['transaction_id']
            ).first()
            if not payment:
                payment = Payment(
                    order_id=payment_data['order'].id,
                    amount=payment_data['amount'],
                    payment_method=payment_data['payment_method'],
                    transaction_id=payment_data['transaction_id'],
                    status=payment_data['status'],
                    created_at=payment_data['created_at']
                )
                db.session.add(payment)
        
        db.session.commit()

        # ========== LOYALTY TRANSACTIONS ==========
        loyalty_transactions_data = [
            {
                'user': users['customer@qaffee.com'],
                'points': 145,  # 1 point per 10 KSh spent
                'transaction_type': LoyaltyPoints.ORDER_COMPLETED,
                'description': f'Points for order #{Order.query.first().id}',
                'order': Order.query.first(),
                'created_at': datetime.now(timezone.utc)
            }
        ]

        for lt_data in loyalty_transactions_data:
            lt = LoyaltyTransaction.query.filter_by(
                user_id=lt_data['user'].id,
                order_id=lt_data['order'].id
            ).first()
            if not lt:
                lt = LoyaltyTransaction(
                    user_id=lt_data['user'].id,
                    points=lt_data['points'],
                    transaction_type=lt_data['transaction_type'],
                    description=lt_data['description'],
                    order_id=lt_data['order'].id,
                    created_at=lt_data['created_at']
                )
                db.session.add(lt)
        
        db.session.commit()

        # ========== REWARD CLAIMS ==========
        reward_claims_data = [
            {
                'user': users['customer@qaffee.com'],
                'reward': rewards['Free Appetizer'],
                'points_spent': 100,
                'status': 'active',
                'expires_at': datetime.now(timezone.utc) + timedelta(days=30),
                'claimed_at': datetime.now(timezone.utc)
            }
        ]

        for rc_data in reward_claims_data:
            rc = RewardClaim.query.filter_by(
                user_id=rc_data['user'].id,
                reward_id=rc_data['reward'].id
            ).first()
            if not rc:
                rc = RewardClaim(
                    user_id=rc_data['user'].id,
                    reward_id=rc_data['reward'].id,
                    points_spent=rc_data['points_spent'],
                    status=rc_data['status'],
                    expires_at=rc_data['expires_at'],
                    claimed_at=rc_data['claimed_at']
                )
                db.session.add(rc)
        
        db.session.commit()

        # ========== REFERRAL CODES ==========
        referral_codes_data = [
            {
                'code': 'JOHNDOE123',
                'user': users['customer@qaffee.com'],
                'points_reward': 100,
                'max_uses': 10,
                'current_uses': 0,
                'is_active': True,
                'expires_at': datetime.now(timezone.utc) + timedelta(days=365),
                'created_at': datetime.now(timezone.utc)
            }
        ]

        for rc_data in referral_codes_data:
            rc = ReferralCode.query.filter_by(code=rc_data['code']).first()
            if not rc:
                rc = ReferralCode(
                    code=rc_data['code'],
                    user_id=rc_data['user'].id,
                    points_reward=rc_data['points_reward'],
                    max_uses=rc_data['max_uses'],
                    current_uses=rc_data['current_uses'],
                    is_active=rc_data['is_active'],
                    expires_at=rc_data['expires_at'],
                    created_at=rc_data['created_at']
                )
                db.session.add(rc)
        
        db.session.commit()

        # ========== REFERRALS ==========
        referrals_data = [
            {
                'referrer': users['customer@qaffee.com'],
                'referred': users['customer2@qaffee.com'],
                'status': 'completed',
                'points_awarded': True,
                'created_at': datetime.now(timezone.utc) - timedelta(days=5),
                'completed_at': datetime.now(timezone.utc) - timedelta(days=4)
            }
        ]

        for ref_data in referrals_data:
            ref = Referral.query.filter_by(
                referrer_id=ref_data['referrer'].id,
                referred_id=ref_data['referred'].id
            ).first()
            if not ref:
                ref = Referral(
                    referrer_id=ref_data['referrer'].id,
                    referred_id=ref_data['referred'].id,
                    status=ref_data['status'],
                    points_awarded=ref_data['points_awarded'],
                    created_at=ref_data['created_at'],
                    completed_at=ref_data['completed_at']
                )
                db.session.add(ref)
        
        db.session.commit()

        # ========== REFERRAL USES ==========
        referral_uses_data = [
            {
                'referral_code': ReferralCode.query.filter_by(code='JOHNDOE123').first(),
                'referred_user': users['customer2@qaffee.com'],
                'points_awarded': 100,
                'status': 'completed',
                'completed_at': datetime.now(timezone.utc) - timedelta(days=4),
                'created_at': datetime.now(timezone.utc) - timedelta(days=5)
            }
        ]

        for ru_data in referral_uses_data:
            ru = ReferralUse.query.filter_by(
                referral_code_id=ru_data['referral_code'].id,
                referred_user_id=ru_data['referred_user'].id
            ).first()
            if not ru:
                ru = ReferralUse(
                    referral_code_id=ru_data['referral_code'].id,
                    referred_user_id=ru_data['referred_user'].id,
                    points_awarded=ru_data['points_awarded'],
                    status=ru_data['status'],
                    completed_at=ru_data['completed_at'],
                    created_at=ru_data['created_at']
                )
                db.session.add(ru)
        
        db.session.commit()

        # ========== REVIEWS (UPDATED) ==========
        reviews_data = [
            {
                'user': users['customer@qaffee.com'],
                'menu_item': menu_items['Hummus'],
                'rating': 5,
                'comment': 'Amazing hummus! Perfect with the warm pita bread.',
                'created_at': datetime.now(timezone.utc) - timedelta(days=1)
            }
        ]

        for review_data in reviews_data:
            review = Review.query.filter_by(
                user_id=review_data['user'].id,
                menu_item_id=review_data['menu_item'].id,
                created_at=review_data['created_at']
            ).first()
            if not review:
                review = Review(
                    user_id=review_data['user'].id,
                    menu_item_id=review_data['menu_item'].id,
                    rating=review_data['rating'],
                    comment=review_data['comment'],
                    created_at=review_data['created_at']
                )
                db.session.add(review)
        
        db.session.commit()

        # ========== NOTIFICATIONS ==========
        notifications_data = [
            {
                'user': users['customer@qaffee.com'],
                'title': 'Order Confirmed',
                'message': 'Your order #123 has been confirmed',
                'type': NotificationType.ORDER_UPDATE,
                'is_read': False,
                'created_at': datetime.now(timezone.utc)
            }
        ]

        for notif_data in notifications_data:
            notif = Notification.query.filter_by(
                user_id=notif_data['user'].id,
                title=notif_data['title'],
                created_at=notif_data['created_at']
            ).first()
            if not notif:
                notif = Notification(
                    user_id=notif_data['user'].id,
                    title=notif_data['title'],
                    message=notif_data['message'],
                    type=notif_data['type'],
                    is_read=notif_data['is_read'],
                    created_at=notif_data['created_at']
                )
                db.session.add(notif)
        
        db.session.commit()

        # ========== SUPPORT TICKETS ==========
        support_tickets_data = [
            {
                'user': users['customer@qaffee.com'],
                'subject': 'Missing item in my order',
                'description': 'I received my order but the Falafel Plate was missing',
                'status': TicketStatus.RESOLVED,
                'priority': TicketPriority.MEDIUM,
                'category': 'order',
                'assigned_to': users['staff@qaffee.com'].id,
                'messages': [
                    {
                        'sender': 'customer',
                        'message': 'Hello, my Falafel Plate was missing from my order',
                        'timestamp': (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
                    },
                    {
                        'sender': 'staff',
                        'message': 'We apologize for the inconvenience. We will refund the item.',
                        'timestamp': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
                    }
                ],
                'created_at': datetime.now(timezone.utc) - timedelta(hours=4),
                'updated_at': datetime.now(timezone.utc) - timedelta(hours=1)
            }
        ]

        for ticket_data in support_tickets_data:
            ticket = SupportTicket.query.filter_by(
                user_id=ticket_data['user'].id,
                subject=ticket_data['subject']
            ).first()
            if not ticket:
                ticket = SupportTicket(
                    user_id=ticket_data['user'].id,
                    subject=ticket_data['subject'],
                    description=ticket_data['description'],
                    status=ticket_data['status'],
                    priority=ticket_data['priority'],
                    category=ticket_data['category'],
                    assigned_to=ticket_data['assigned_to'],
                    messages=ticket_data['messages'],
                    created_at=ticket_data['created_at'],
                    updated_at=ticket_data['updated_at']
                )
                db.session.add(ticket)
        
        db.session.commit()

        # ========== FEEDBACK ==========
        feedback_data = [
            {
                'user': users['customer@qaffee.com'],
                'rating': 4,
                'comment': 'Great service but the delivery was a bit late',
                'category': 'service',
                'created_at': datetime.now(timezone.utc) - timedelta(hours=2)
            }
        ]

        for fb_data in feedback_data:
            fb = Feedback.query.filter_by(
                user_id=fb_data['user'].id,
                created_at=fb_data['created_at']
            ).first()
            if not fb:
                fb = Feedback(
                    user_id=fb_data['user'].id,
                    rating=fb_data['rating'],
                    comment=fb_data['comment'],
                    category=fb_data['category'],
                    created_at=fb_data['created_at']
                )
                db.session.add(fb)
        
        db.session.commit()

        # ========== STORE LOCATIONS ==========
        store_locations_data = [
            {
                'name': 'Downtown Cafe',
                'address': '456 Downtown Ave, Cityville',
                'city': 'Cityville',
                'state': 'State',
                'postal_code': '12345',
                'country': 'Country',
                'phone': '123-456-7890',
                'email': 'downtown@qaffee.com',
                'latitude': 40.7128,
                'longitude': -74.0060,
                'opening_hours': {
                    'monday': '7:00 AM - 8:00 PM',
                    'tuesday': '7:00 AM - 8:00 PM',
                    'wednesday': '7:00 AM - 8:00 PM',
                    'thursday': '7:00 AM - 9:00 PM',
                    'friday': '7:00 AM - 9:00 PM',
                    'saturday': '8:00 AM - 9:00 PM',
                    'sunday': '8:00 AM - 6:00 PM'
                },
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]

        for store_data in store_locations_data:
            store = StoreLocation.query.filter_by(name=store_data['name']).first()
            if not store:
                store = StoreLocation(**store_data)
                db.session.add(store)
        
        db.session.commit()

        # ========== FAQS ==========
        faqs_data = [
            {
                'question': 'How do I place an order?',
                'answer': 'You can place an order through our website or mobile app.',
                'category': 'ordering',
                'order': 1,
                'is_published': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept credit cards, debit cards, and mobile payments.',
                'category': 'payment',
                'order': 2,
                'is_published': True,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc)
            }
        ]

        for faq_data in faqs_data:
            faq = FAQ.query.filter_by(question=faq_data['question']).first()
            if not faq:
                faq = FAQ(**faq_data)
                db.session.add(faq)
        
        db.session.commit()

        print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed_data()