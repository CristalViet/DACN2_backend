"""
Script to seed sample data into the database.
Run: python seed_data.py
"""
from sqlalchemy.orm import Session
from datetime import date, datetime, timezone
from decimal import Decimal

from app.database import SessionLocal, engine, Base
from app.models import (
    user_role, user, category, author, publisher, book,
    order, order_detail, summary, content_section, comment, admin_comment,
    cart, cart_item
)
from app.core.security import get_password_hash
from app.models.order import PaymentStatus, ShipmentStatus
from app.models.comment import CommentAccess

Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

def seed_data():
    """Seed all sample data"""
    db: Session = SessionLocal()
    
    try:
        print("🌱 Starting data seeding...")
        
        # 1. User Roles
        print("📝 Creating User Roles...")
        admin_role = user_role.UserRole(
            role_name="admin",
            permissions="all"
        )
        user_role_obj = user_role.UserRole(
            role_name="reader",
            permissions="read"
        )
        writer_role_obj = user_role.UserRole(
            role_name="writer",
            permissions="write"
        )
        db.add(admin_role)
        db.add(user_role_obj)
        db.add(writer_role_obj)
        db.commit()
        db.refresh(admin_role)
        db.refresh(user_role_obj)
        db.refresh(writer_role_obj)
        print(f"✅ Created {db.query(user_role.UserRole).count()} roles")
        
        # 2. Users
        print("👥 Creating Users...")
        admin_user = user.User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            phone="0123456789",
            role_id=admin_role.id,
            profile_image="https://via.placeholder.com/150",
            bio="System administrator",
            is_active=True
        )
        
        writer_user = user.User(
            username="writer_user",
            email="writer@example.com",
            password_hash=get_password_hash("password123"),
            phone="0987654321",
            role_id=writer_role_obj.id,
            profile_image="https://via.placeholder.com/150",
            bio="A book writer",
            is_active=True
        )
        reader_user = user.User(
            username="reader_user",
            email="reader@example.com",
            password_hash=get_password_hash("password123"),
            phone="0912345678",
            role_id=user_role_obj.id,
            bio="Professional book reviewer",
            is_active=True
        )
        
        db.add(admin_user)
        db.add(writer_user)
        db.add(reader_user)
        db.commit()
        db.refresh(admin_user)
        db.refresh(writer_user)
        db.refresh(reader_user)
        print(f"✅ Created {db.query(user.User).count()} users")
        
        # 3. Categories
        print("📚 Creating Categories...")
        categories_data = [
            {"category_name": "Novel"},
            {"category_name": "Science"},
            {"category_name": "History"},
            {"category_name": "Business"},
            {"category_name": "Self Development"},
            {"category_name": "Technology"},
            {"category_name": "Fiction"},
            {"category_name": "Psychology"},
            {"category_name": "Philosophy"},
            {"category_name": "Biography"},
            {"category_name": "Economics"},
            {"category_name": "Programming"},
        ]
        categories = []
        for cat_data in categories_data:
            cat = category.Category(**cat_data)
            db.add(cat)
            categories.append(cat)
        db.commit()
        for cat in categories:
            db.refresh(cat)
        print(f"✅ Created {len(categories)} categories")
        
        # 4. Authors
        print("✍️ Creating Authors...")
        authors_data = [
            {
                "name": "Nguyen Nhat Anh",
                "birth_date": date(1955, 5, 7),
                "nationality": "Vietnam",
                "biography": "Famous Vietnamese writer known for childhood themes"
            },
            {
                "name": "Yuval Noah Harari",
                "birth_date": date(1976, 2, 24),
                "nationality": "Israel",
                "biography": "Historian and popular author on the history of humankind"
            },
            {
                "name": "Dale Carnegie",
                "birth_date": date(1888, 11, 24),
                "nationality": "USA",
                "biography": "Famous author on personal development and communication skills"
            },
            {
                "name": "Stephen King",
                "birth_date": date(1947, 9, 21),
                "nationality": "USA",
                "biography": "Master of horror and suspense fiction"
            },
            {
                "name": "J.K. Rowling",
                "birth_date": date(1965, 7, 31),
                "nationality": "UK",
                "biography": "Author of the famous Harry Potter series"
            },
            {
                "name": "Daniel Kahneman",
                "birth_date": date(1934, 3, 5),
                "nationality": "Israel",
                "biography": "Nobel Prize winner in Economics, expert in behavioral psychology"
            },
            {
                "name": "Malcolm Gladwell",
                "birth_date": date(1963, 9, 3),
                "nationality": "Canada",
                "biography": "Journalist and author known for popular science and psychology books"
            },
            {
                "name": "Robert Kiyosaki",
                "birth_date": date(1947, 4, 8),
                "nationality": "USA",
                "biography": "Entrepreneur and author of Rich Dad Poor Dad"
            },
            {
                "name": "Elon Musk",
                "birth_date": date(1971, 6, 28),
                "nationality": "South Africa",
                "biography": "Entrepreneur and CEO of Tesla and SpaceX"
            },
            {
                "name": "Bill Gates",
                "birth_date": date(1955, 10, 28),
                "nationality": "USA",
                "biography": "Co-founder of Microsoft and philanthropist"
            },
            {
                "name": "Walter Isaacson",
                "birth_date": date(1952, 5, 20),
                "nationality": "USA",
                "biography": "Biographer and journalist, author of Steve Jobs biography"
            },
            {
                "name": "James Clear",
                "birth_date": date(1986, 1, 22),
                "nationality": "USA",
                "biography": "Author of Atomic Habits, expert in habit formation"
            },
            {
                "name": "Eric Ries",
                "birth_date": date(1978, 9, 22),
                "nationality": "USA",
                "biography": "Entrepreneur and author of The Lean Startup methodology"
            },
            {
                "name": "Robert C. Martin",
                "birth_date": date(1952, 12, 5),
                "nationality": "USA",
                "biography": "Software engineer and author, known as Uncle Bob, expert in clean code"
            },
            {
                "name": "Andrew Hunt",
                "birth_date": date(1964, 3, 4),
                "nationality": "USA",
                "biography": "Software developer and co-author of The Pragmatic Programmer"
            },
            {
                "name": "Clayton Christensen",
                "birth_date": date(1952, 4, 6),
                "nationality": "USA",
                "biography": "Harvard Business School professor, author of The Innovator's Dilemma"
            },
            {
                "name": "Jared Diamond",
                "birth_date": date(1937, 9, 10),
                "nationality": "USA",
                "biography": "Geographer and author of Guns, Germs, and Steel"
            },
            {
                "name": "William L. Shirer",
                "birth_date": date(1904, 2, 23),
                "nationality": "USA",
                "biography": "Journalist and historian, author of The Rise and Fall of the Third Reich"
            },
            {
                "name": "Ashlee Vance",
                "birth_date": date(1977, 1, 1),
                "nationality": "USA",
                "biography": "Journalist and author of Elon Musk biography"
            },
            {
                "name": "Stephen Covey",
                "birth_date": date(1932, 10, 24),
                "nationality": "USA",
                "biography": "Author and educator, best known for The 7 Habits of Highly Effective People"
            },
        ]
        authors = []
        for author_data in authors_data:
            auth = author.Author(**author_data)
            db.add(auth)
            authors.append(auth)
        db.commit()
        for auth in authors:
            db.refresh(auth)
        print(f"✅ Created {len(authors)} authors")
        
        # 5. Publishers
        print("🏢 Creating Publishers...")
        publishers_data = [
            {"name": "Tre Publishing House"},
            {"name": "Kim Dong Publishing House"},
            {"name": "Writers' Association Publishing House"},
            {"name": "The World Publishing House"},
            {"name": "Penguin Random House"},
            {"name": "HarperCollins"},
            {"name": "Simon & Schuster"},
            {"name": "Hachette Book Group"},
        ]
        publishers = []
        for pub_data in publishers_data:
            pub = publisher.Publisher(**pub_data)
            db.add(pub)
            publishers.append(pub)
        db.commit()
        for pub in publishers:
            db.refresh(pub)
        print(f"✅ Created {len(publishers)} publishers")
        
        # 6. Books
        print("📖 Creating Books...")
        books_data = [
            # Novel cluster
            {
  "title": "Yellow Flowers on the Green Grass",
  "category_ids": [categories[0].id],
  "author_ids": [authors[0].id],
  "publisher_id": publishers[0].id,
  "publish_date": "2010-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9786046981100-M.jpg",
  "price": 120000,
  "stock_quantity": 50
},
{
  "title": "The Book Thief",
  "category_ids": [categories[0].id],
  "author_ids": [authors[0].id],
  "publisher_id": publishers[1].id,
  "publish_date": "2005-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780375842207-M.jpg",
  "price": 180000,
  "stock_quantity": 25
},
{
  "title": "The Shining",
  "category_ids": [categories[6].id],
  "author_ids": [authors[3].id],
  "publisher_id": publishers[4].id,
  "publish_date": "1977-01-28",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780385121675-M.jpg",
  "price": 200000,
  "stock_quantity": 40
},
{
  "title": "Harry Potter and the Philosopher's Stone",
  "category_ids": [categories[6].id],
  "author_ids": [authors[4].id],
  "publisher_id": publishers[5].id,
  "publish_date": "1997-06-26",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780747532743-M.jpg",
  "price": 220000,
  "stock_quantity": 100
},
{
  "title": "Sapiens: A Brief History of Humankind",
  "category_ids": [categories[1].id],
  "author_ids": [authors[1].id],
  "publisher_id": publishers[3].id,
  "publish_date": "2011-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780062316097-M.jpg",
  "price": 250000,
  "stock_quantity": 30
},
{
  "title": "Homo Deus: A Brief History of Tomorrow",
  "category_ids": [categories[1].id],
  "author_ids": [authors[1].id],
  "publisher_id": publishers[3].id,
  "publish_date": "2015-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780062464316-M.jpg",
  "price": 260000,
  "stock_quantity": 35
},
{
  "title": "21 Lessons for the 21st Century",
  "category_ids": [categories[1].id],
  "author_ids": [authors[1].id],
  "publisher_id": publishers[3].id,
  "publish_date": "2018-08-30",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780525512172-M.jpg",
  "price": 270000,
  "stock_quantity": 28
},
{
  "title": "Thinking, Fast and Slow",
  "category_ids": [categories[7].id],
  "author_ids": [authors[5].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2011-10-25",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780374275631-M.jpg",
  "price": 280000,
  "stock_quantity": 45
},
{
  "title": "Outliers: The Story of Success",
  "category_ids": [categories[7].id],
  "author_ids": [authors[6].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2008-11-18",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780316017930-M.jpg",
  "price": 240000,
  "stock_quantity": 50
},
{
  "title": "Blink: The Power of Thinking Without Thinking",
  "category_ids": [categories[7].id],
  "author_ids": [authors[6].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2005-01-11",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780316010665-M.jpg",
  "price": 230000,
  "stock_quantity": 42
},
{
  "title": "The Tipping Point",
  "category_ids": [categories[7].id],
  "author_ids": [authors[6].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2000-03-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780316346627-M.jpg",
  "price": 220000,
  "stock_quantity": 38
},
{
  "title": "Rich Dad Poor Dad",
  "category_ids": [categories[3].id],
  "author_ids": [authors[7].id],
  "publisher_id": publishers[6].id,
  "publish_date": "1997-04-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9781612680019-M.jpg",
  "price": 190000,
  "stock_quantity": 80
},
{
  "title": "Cashflow Quadrant",
  "category_ids": [categories[3].id],
  "author_ids": [authors[7].id],
  "publisher_id": publishers[6].id,
  "publish_date": "1998-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9781612680057-M.jpg",
  "price": 200000,
  "stock_quantity": 60
},
{
  "title": "The Lean Startup",
  "category_ids": [categories[3].id],
  "author_ids": [authors[12].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2011-09-13",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780307887894-M.jpg",
  "price": 250000,
  "stock_quantity": 55
},
{
  "title": "How to Win Friends & Influence People",
  "category_ids": [categories[4].id],
  "author_ids": [authors[2].id],
  "publisher_id": publishers[3].id,
  "publish_date": "1936-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780671027032-M.jpg",
  "price": 150000,
  "stock_quantity": 100
},
{
  "title": "Atomic Habits",
  "category_ids": [categories[4].id],
  "author_ids": [authors[11].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2018-10-16",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780735211292-M.jpg",
  "price": 210000,
  "stock_quantity": 90
},
{
  "title": "The 7 Habits of Highly Effective People",
  "category_ids": [categories[4].id],
  "author_ids": [authors[19].id],
  "publisher_id": publishers[3].id,
  "publish_date": "1989-08-15",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780743269513-M.jpg",
  "price": 180000,
  "stock_quantity": 75
},
{
  "title": "The Innovator's Dilemma",
  "category_ids": [categories[5].id],
  "author_ids": [authors[15].id],
  "publisher_id": publishers[4].id,
  "publish_date": "1997-01-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780062060242-M.jpg",
  "price": 290000,
  "stock_quantity": 40
},
{
  "title": "Clean Code",
  "category_ids": [categories[11].id],
  "author_ids": [authors[13].id],
  "publisher_id": publishers[7].id,
  "publish_date": "2008-08-11",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780132350884-M.jpg",
  "price": 320000,
  "stock_quantity": 65
},
{
  "title": "The Pragmatic Programmer",
  "category_ids": [categories[11].id],
  "author_ids": [authors[14].id],
  "publisher_id": publishers[7].id,
  "publish_date": "1999-10-20",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780201616224-M.jpg",
  "price": 300000,
  "stock_quantity": 55
},
{
  "title": "Guns, Germs, and Steel",
  "category_ids": [categories[2].id],
  "author_ids": [authors[16].id],
  "publisher_id": publishers[3].id,
  "publish_date": "1997-03-01",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780393317558-M.jpg",
  "price": 270000,
  "stock_quantity": 35
},
{
  "title": "The Rise and Fall of the Third Reich",
  "category_ids": [categories[2].id],
  "author_ids": [authors[17].id],
  "publisher_id": publishers[3].id,
  "publish_date": "1960-10-17",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780671728687-M.jpg",
  "price": 310000,
  "stock_quantity": 30
},
{
  "title": "Steve Jobs",
  "category_ids": [categories[9].id],
  "author_ids": [authors[10].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2011-10-24",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9781451648539-M.jpg",
  "price": 300000,
  "stock_quantity": 50
},
{
  "title": "Elon Musk: Tesla, SpaceX, and the Quest for a Fantastic Future",
  "category_ids": [categories[9].id],
  "author_ids": [authors[18].id],
  "publisher_id": publishers[4].id,
  "publish_date": "2015-05-19",
  "cover_image": "https://covers.openlibrary.org/b/isbn/9780062301239-M.jpg",
  "price": 280000,
  "stock_quantity": 45
}
        ]

        books = []
        for book_data in books_data:
            # Extract many-to-many relationship data
            category_ids = book_data.pop("category_ids", [])
            author_ids = book_data.pop("author_ids", [])
            
            # Create book with remaining data
            b = book.Book(**book_data)
            db.add(b)
            db.flush()  # Flush to get the book ID
            
            # Set many-to-many relationships
            if category_ids:
                b.categories = [cat for cat in categories if cat.id in category_ids]
            if author_ids:
                b.authors = [auth for auth in authors if auth.id in author_ids]
            
            books.append(b)
        db.commit()
        for b in books:
            db.refresh(b)
        print(f"✅ Created {len(books)} books")
        
        # 7. Carts
        print("🛒 Creating Carts...")
        cart1 = cart.Cart(user_id=writer_user.id)
        cart2 = cart.Cart(user_id=reader_user.id)
        db.add(cart1)
        db.add(cart2)
        db.commit()
        db.refresh(cart1)
        db.refresh(cart2)
        print(f"✅ Created {db.query(cart.Cart).count()} carts")
        
        # 8. Cart Items
        print("🛍️ Creating Cart Items...")
        cart_items_data = [
            {
                "cart_id": cart1.id,
                "book_id": books[0].id,
                "quantity": 1,
                "price": Decimal("120000")
            },
            {
                "cart_id": cart1.id,
                "book_id": books[2].id,
                "quantity": 2,
                "price": Decimal("150000")
            },
            {
                "cart_id": cart2.id,
                "book_id": books[1].id,
                "quantity": 1,
                "price": Decimal("250000")
            },
        ]
        for ci_data in cart_items_data:
            ci = cart_item.CartItem(**ci_data)
            db.add(ci)
        db.commit()
        print(f"✅ Created {db.query(cart_item.CartItem).count()} cart items")
        
        # 9. Orders
        print("📦 Creating Orders...")
        from datetime import timedelta
        order1 = order.Order(
            user_id=writer_user.id,
            total_amount=Decimal("300000"),
            payment_method="Credit Card",
            payment_status=PaymentStatus.COMPLETED,
            recipient_name="John Doe",
            address="123 Main Street, City",
            phone="0987654321",
            shipment_status=ShipmentStatus.SHIPPED,
            delivery_date=datetime.now(timezone.utc) + timedelta(days=3),
            shipping_method="Standard"
        )
        order2 = order.Order(
            user_id=reader_user.id,
            total_amount=Decimal("430000"),
            payment_method="Bank Transfer",
            payment_status=PaymentStatus.PENDING,
            recipient_name="Jane Smith",
            address="456 Oak Avenue, City",
            phone="0912345678",
            shipment_status=ShipmentStatus.PENDING,
            shipping_method="Express"
        )
        db.add(order1)
        db.add(order2)
        db.commit()
        db.refresh(order1)
        db.refresh(order2)
        print(f"✅ Created {db.query(order.Order).count()} orders")
        
        # 10. Order Details
        print("📋 Creating Order Details...")
        order_details_data = [
            {
                "order_id": order1.id,
                "book_id": books[0].id,
                "quantity": 2,
                "price": Decimal("120000")
            },
            {
                "order_id": order1.id,
                "book_id": books[2].id,
                "quantity": 1,
                "price": Decimal("150000")
            },
            {
                "order_id": order2.id,
                "book_id": books[1].id,
                "quantity": 1,
                "price": Decimal("250000")
            },
            {
                "order_id": order2.id,
                "book_id": books[3].id,
                "quantity": 1,
                "price": Decimal("180000")
            },
        ]
        for od_data in order_details_data:
            od = order_detail.OrderDetail(**od_data)
            db.add(od)
        db.commit()
        print(f"✅ Created {db.query(order_detail.OrderDetail).count()} order details")
        
        # 11. Summaries (in clusters for recommendation testing)
        print("📄 Creating Summaries...")
        from datetime import timedelta
        base_time = datetime.now(timezone.utc)
        
        summaries_data = [
            # Novel cluster - multiple summaries for novel books
            {
                "title": "Summary: Yellow Flowers on the Green Grass",
                "book_id": books[0].id,
                "published_date": base_time - timedelta(days=10),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.5,
                "read_count": 1200,
                "audio_url": "https://example.com/audio_summary1.mp3"
            },
            {
                "title": "Complete Analysis: Yellow Flowers on the Green Grass",
                "book_id": books[0].id,
                "published_date": base_time - timedelta(days=5),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 850,
                "audio_url": "https://example.com/audio_summary_novel1.mp3"
            },
            {
                "title": "Summary: The Book Thief",
                "book_id": books[1].id,
                "published_date": base_time - timedelta(days=8),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.6,
                "read_count": 1500,
                "audio_url": "https://example.com/audio_summary_novel2.mp3"
            },
            {
                "title": "Summary: The Shining",
                "book_id": books[2].id,
                "published_date": base_time - timedelta(days=7),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.4,
                "read_count": 2000,
                "audio_url": "https://example.com/audio_summary_fiction1.mp3"
            },
            {
                "title": "Summary: Harry Potter and the Philosopher's Stone",
                "book_id": books[3].id,
                "published_date": base_time - timedelta(days=6),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.9,
                "read_count": 5000,
                "audio_url": "https://example.com/audio_summary_fiction2.mp3"
            },
            # Science cluster - multiple summaries for science books
            {
                "title": "Summary: Sapiens - A Brief History of Humankind",
                "book_id": books[4].id,
                "published_date": base_time - timedelta(days=12),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 2500,
                "audio_url": "https://example.com/audio_summary2.mp3"
            },
            {
                "title": "Deep Dive: Sapiens - Understanding Human Evolution",
                "book_id": books[4].id,
                "published_date": base_time - timedelta(days=3),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.9,
                "read_count": 1800,
                "audio_url": "https://example.com/audio_summary_science1.mp3"
            },
            {
                "title": "Summary: Homo Deus - A Brief History of Tomorrow",
                "book_id": books[5].id,
                "published_date": base_time - timedelta(days=9),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 1900,
                "audio_url": "https://example.com/audio_summary_science2.mp3"
            },
            {
                "title": "Summary: 21 Lessons for the 21st Century",
                "book_id": books[6].id,
                "published_date": base_time - timedelta(days=4),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.6,
                "read_count": 1600,
                "audio_url": "https://example.com/audio_summary_science3.mp3"
            },
            # Psychology cluster - multiple summaries for psychology books
            {
                "title": "Summary: Thinking, Fast and Slow",
                "book_id": books[7].id,
                "published_date": base_time - timedelta(days=11),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 3000,
                "audio_url": "https://example.com/audio_summary_psych1.mp3"
            },
            {
                "title": "Key Insights: Thinking, Fast and Slow",
                "book_id": books[7].id,
                "published_date": base_time - timedelta(days=2),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.9,
                "read_count": 2200,
                "audio_url": "https://example.com/audio_summary_psych1b.mp3"
            },
            {
                "title": "Summary: Outliers - The Story of Success",
                "book_id": books[8].id,
                "published_date": base_time - timedelta(days=10),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.5,
                "read_count": 2100,
                "audio_url": "https://example.com/audio_summary_psych2.mp3"
            },
            {
                "title": "Summary: Blink - The Power of Thinking Without Thinking",
                "book_id": books[9].id,
                "published_date": base_time - timedelta(days=8),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.4,
                "read_count": 1800,
                "audio_url": "https://example.com/audio_summary_psych3.mp3"
            },
            {
                "title": "Summary: The Tipping Point",
                "book_id": books[10].id,
                "published_date": base_time - timedelta(days=6),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.6,
                "read_count": 1700,
                "audio_url": "https://example.com/audio_summary_psych4.mp3"
            },
            # Business cluster - multiple summaries for business books
            {
                "title": "Summary: Rich Dad Poor Dad",
                "book_id": books[11].id,
                "published_date": base_time - timedelta(days=13),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 4000,
                "audio_url": "https://example.com/audio_summary_business1.mp3"
            },
            {
                "title": "Financial Wisdom: Rich Dad Poor Dad Explained",
                "book_id": books[11].id,
                "published_date": base_time - timedelta(days=1),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 3200,
                "audio_url": "https://example.com/audio_summary_business1b.mp3"
            },
            {
                "title": "Summary: Cashflow Quadrant",
                "book_id": books[12].id,
                "published_date": base_time - timedelta(days=9),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.6,
                "read_count": 2800,
                "audio_url": "https://example.com/audio_summary_business2.mp3"
            },
            {
                "title": "Summary: The Lean Startup",
                "book_id": books[13].id,
                "published_date": base_time - timedelta(days=7),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.5,
                "read_count": 2600,
                "audio_url": "https://example.com/audio_summary_business3.mp3"
            },
            # Self Development cluster - multiple summaries for self-help books
            {
                "title": "Summary: How to Win Friends & Influence People",
                "book_id": books[14].id,
                "published_date": base_time - timedelta(days=14),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.6,
                "read_count": 3500,
                "audio_url": "https://example.com/audio_summary_selfdev1.mp3"
            },
            {
                "title": "Complete Guide: How to Win Friends & Influence People",
                "book_id": books[14].id,
                "published_date": base_time - timedelta(days=2),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 2900,
                "audio_url": "https://example.com/audio_summary_selfdev1b.mp3"
            },
            {
                "title": "Summary: Atomic Habits",
                "book_id": books[15].id,
                "published_date": base_time - timedelta(days=5),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.9,
                "read_count": 4200,
                "audio_url": "https://example.com/audio_summary_selfdev2.mp3"
            },
            {
                "title": "Summary: The 7 Habits of Highly Effective People",
                "book_id": books[16].id,
                "published_date": base_time - timedelta(days=8),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 3800,
                "audio_url": "https://example.com/audio_summary_selfdev3.mp3"
            },
            # Technology cluster - multiple summaries for tech books
            {
                "title": "Summary: The Innovator's Dilemma",
                "book_id": books[17].id,
                "published_date": base_time - timedelta(days=10),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 2400,
                "audio_url": "https://example.com/audio_summary_tech1.mp3"
            },
            {
                "title": "Summary: Clean Code",
                "book_id": books[18].id,
                "published_date": base_time - timedelta(days=6),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.9,
                "read_count": 3100,
                "audio_url": "https://example.com/audio_summary_prog1.mp3"
            },
            {
                "title": "Summary: The Pragmatic Programmer",
                "book_id": books[19].id,
                "published_date": base_time - timedelta(days=4),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 2700,
                "audio_url": "https://example.com/audio_summary_prog2.mp3"
            },
            # History cluster
            {
                "title": "Summary: Guns, Germs, and Steel",
                "book_id": books[20].id,
                "published_date": base_time - timedelta(days=11),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.6,
                "read_count": 2200,
                "audio_url": "https://example.com/audio_summary_history1.mp3"
            },
            {
                "title": "Summary: The Rise and Fall of the Third Reich",
                "book_id": books[21].id,
                "published_date": base_time - timedelta(days=7),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 1900,
                "audio_url": "https://example.com/audio_summary_history2.mp3"
            },
            # Biography cluster
            {
                "title": "Summary: Steve Jobs Biography",
                "book_id": books[22].id,
                "published_date": base_time - timedelta(days=9),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 3300,
                "audio_url": "https://example.com/audio_summary_bio1.mp3"
            },
            {
                "title": "Summary: Elon Musk - Tesla, SpaceX, and the Quest",
                "book_id": books[23].id,
                "published_date": base_time - timedelta(days=5),
                "user_id": reader_user.id,
                "status": "approved",
                "avg_rating": 4.7,
                "read_count": 2800,
                "audio_url": "https://example.com/audio_summary_bio2.mp3"
            },
            # Some drafts/editing status summaries
            {
                "title": "Summary: How to Win Friends & Influence People (Draft)",
                "book_id": books[14].id,
                "published_date": None,
                "user_id": writer_user.id,
                "status": "editing",
                "avg_rating": 0,
                "read_count": 0,
                "audio_url": None
            },
            {
                "title": "Summary: Atomic Habits (Work in Progress)",
                "book_id": books[15].id,
                "published_date": None,
                "user_id": reader_user.id,
                "status": "editing",
                "avg_rating": 0,
                "read_count": 0,
                "audio_url": None
            },
        ]
        summaries = []
        for summary_data in summaries_data:
            s = summary.Summary(**summary_data)
            db.add(s)
            summaries.append(s)
        db.commit()
        for s in summaries:
            db.refresh(s)
        print(f"✅ Created {len(summaries)} summaries")
        
        # 12. Content Sections
        print("📑 Creating Content Sections...")
        # Add content sections for approved summaries (skip drafts)
        approved_summaries = [s for s in summaries if s.status == "approved"]
        content_sections_data = []
        
        # Find summaries for selected books (5 books with detailed content)
        selected_book_titles = [
            "Sapiens: A Brief History of Humankind",
            "Thinking, Fast and Slow",
            "Rich Dad Poor Dad",
            "Atomic Habits",
            "Clean Code"
        ]
        
        # Create a mapping of book titles to book objects
        book_title_map = {b.title: b for b in books}
        
        # Find summaries for selected books
        selected_summaries = []
        for summ_obj in approved_summaries:
            book_obj = db.query(book.Book).filter(book.Book.id == summ_obj.book_id).first()
            if book_obj and book_obj.title in selected_book_titles:
                # Only take the first summary for each selected book
                if not any(s.book_id == summ_obj.book_id for s in selected_summaries):
                    selected_summaries.append(summ_obj)
        
        # Create detailed content sections for selected 5 books
        for summ_obj in selected_summaries:
            book_obj = db.query(book.Book).filter(book.Book.id == summ_obj.book_id).first()
            if not book_obj:
                continue
                
            if book_obj.title == "Sapiens: A Brief History of Humankind":
                content_sections_data.extend([
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 1,
                        "title": "Introduction: The Cognitive Revolution",
                        "content": "Sapiens: A Brief History of Humankind by Yuval Noah Harari is a groundbreaking exploration of how Homo sapiens came to dominate the world. The book begins with the Cognitive Revolution, which occurred around 70,000 years ago. This revolution enabled humans to develop language, share complex information, and cooperate in large groups. Unlike other animals, humans could discuss things that didn't exist, creating shared myths and beliefs that bound communities together. This ability to believe in fictional entities like gods, nations, and corporations allowed humans to organize in groups of thousands, far beyond the natural limit of about 150 individuals that other primates can manage. The Cognitive Revolution marked the beginning of human history, setting the stage for all subsequent developments in human civilization.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_1.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 2,
                        "title": "The Agricultural Revolution and Its Consequences",
                        "content": "The Agricultural Revolution, beginning around 12,000 years ago, transformed human society in ways that were both beneficial and detrimental. While agriculture allowed humans to settle in permanent communities and support larger populations, it also led to harder work, poorer nutrition, and increased vulnerability to disease. Harari provocatively argues that the Agricultural Revolution was 'history's biggest fraud' because it made the average person's life worse, not better. However, it was necessary for the development of complex societies. The surplus food produced by agriculture enabled the creation of cities, kingdoms, and empires. It also led to the development of writing, mathematics, and complex social hierarchies. The Agricultural Revolution fundamentally changed humanity's relationship with the environment and with each other, creating the foundation for modern civilization.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_2.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 3,
                        "title": "The Unification of Humankind and Scientific Revolution",
                        "content": "Harari explains how three universal orders - money, empires, and religion - gradually unified humankind into a single global society. Money created a universal medium of exchange that transcended cultural barriers. Empires spread common cultures and laws across vast territories. Religions provided shared ethical codes and worldviews. The Scientific Revolution, beginning around 500 years ago, marked another turning point. Unlike previous knowledge systems, science admitted ignorance and actively sought new discoveries. This led to unprecedented technological progress and European global dominance. However, Harari warns that this progress came at a cost: the destruction of traditional ways of life, environmental degradation, and the potential for catastrophic consequences. The book challenges readers to consider whether humanity's progress has truly made us happier and whether we can control the forces we've unleashed.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_3.mp3"
                    }
                ])
            elif book_obj.title == "Thinking, Fast and Slow":
                content_sections_data.extend([
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 1,
                        "title": "Introduction: Two Systems of Thinking",
                        "content": "Nobel Prize winner Daniel Kahneman introduces us to two distinct systems that drive our thinking. System 1 operates automatically and quickly, with little or no effort and no sense of voluntary control. It handles tasks like detecting hostility in a voice, reading words on billboards, and making simple calculations. System 2 allocates attention to effortful mental activities that demand it, including complex computations. It's associated with the subjective experience of agency, choice, and concentration. Most of what we think and do originates in System 1, but System 2 takes over when things get difficult. However, System 2 is lazy and often accepts what System 1 tells it. This division of labor between the two systems is highly efficient, but it leads to systematic errors in our thinking. Understanding these systems helps us recognize when we're making cognitive mistakes and how to think more clearly.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_1.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 2,
                        "title": "Heuristics and Biases: How We Make Decisions",
                        "content": "Kahneman reveals numerous cognitive biases that affect our judgment. The availability heuristic makes us overestimate the probability of events that are easily recalled from memory. The anchoring effect causes us to rely too heavily on the first piece of information we encounter. The representativeness heuristic leads us to judge probabilities by similarity rather than statistical likelihood. Confirmation bias makes us seek information that confirms our existing beliefs. Loss aversion means we feel losses more strongly than equivalent gains, leading to risk-averse behavior. The framing effect shows how the same information presented differently can lead to different decisions. These biases aren't random errors but systematic patterns in how our minds work. They served us well in our evolutionary past but can lead to poor decisions in the modern world. By understanding these biases, we can recognize them in ourselves and others, and make better decisions.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_2.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 3,
                        "title": "Overconfidence and Prospect Theory",
                        "content": "Kahneman demonstrates how overconfidence affects our judgments and decisions. We consistently overestimate our abilities, the accuracy of our predictions, and our control over events. This overconfidence is partly due to System 1's tendency to create coherent stories from limited information. We also suffer from the planning fallacy, consistently underestimating how long projects will take and how much they will cost. Prospect Theory, for which Kahneman won the Nobel Prize, explains how people actually make decisions under uncertainty, contradicting traditional economic theory. People evaluate outcomes relative to a reference point (usually the status quo) rather than in absolute terms. They're risk-averse when facing gains but risk-seeking when facing losses. This explains many seemingly irrational behaviors in economics and everyday life. The book concludes that while we can't eliminate these cognitive biases, awareness of them can help us make better decisions and design better systems.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_3.mp3"
                    }
                ])
            elif book_obj.title == "Rich Dad Poor Dad":
                content_sections_data.extend([
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 1,
                        "title": "Introduction: Two Different Perspectives on Money",
                        "content": "Robert Kiyosaki tells the story of growing up with two father figures who had completely different attitudes toward money and wealth. His 'poor dad' (his biological father) was highly educated, worked hard as a government employee, but struggled financially throughout his life. His 'rich dad' (his best friend's father) had less formal education but became one of the wealthiest men in Hawaii. The fundamental difference was their mindset: poor dad believed in working for money, while rich dad believed in making money work for him. Poor dad said 'I can't afford it' and focused on job security, while rich dad asked 'How can I afford it?' and focused on financial education. This contrast sets up the book's central theme: that financial literacy and the right mindset are more important than a high salary. The book challenges conventional wisdom about money, education, and success, arguing that the school system doesn't teach financial literacy, leaving most people trapped in the 'rat race' of working for money.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_1.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 2,
                        "title": "Key Principles: Assets vs Liabilities and Making Money Work for You",
                        "content": "Kiyosaki's most important lesson is understanding the difference between assets and liabilities. An asset puts money in your pocket, while a liability takes money out. Most people think their house is an asset, but Kiyosaki argues it's actually a liability because it takes money out of your pocket through mortgage payments, taxes, and maintenance. The rich focus on acquiring income-generating assets like rental properties, stocks, bonds, and businesses. The poor and middle class focus on acquiring liabilities that they think are assets, like houses, cars, and consumer goods. Rich dad taught Kiyosaki to 'mind your own business' - meaning build and maintain your asset column, not your employer's. While working a job, you should be building your own asset base. The goal is to have your assets generate enough income to cover your expenses, achieving financial freedom. This requires financial education, taking calculated risks, and thinking like an investor rather than an employee.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_2.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 3,
                        "title": "Overcoming Obstacles and Taking Action",
                        "content": "Kiyosaki identifies five main obstacles that prevent people from achieving financial independence: fear, cynicism, laziness, bad habits, and arrogance. Fear of losing money prevents most people from investing, but the rich understand that failure is part of the learning process. Cynicism creates doubt and inaction. Laziness manifests as being too busy to manage your finances. Bad habits, especially poor spending habits, keep people poor. Arrogance means thinking you know everything and not seeking advice. To overcome these obstacles, you need to develop financial intelligence through education, start small, and learn from mistakes. Kiyosaki emphasizes that the most important investment is in your financial education. You should read books, attend seminars, and learn from successful investors. The book concludes with actionable steps: stop doing what you're doing, look for new ideas, find someone who has done what you want to do, take classes and buy tapes, make lots of offers, and take action. The key is to start now, even with small steps, and continuously educate yourself about money and investing.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_3.mp3"
                    }
                ])
            elif book_obj.title == "Atomic Habits":
                content_sections_data.extend([
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 1,
                        "title": "Introduction: The Surprising Power of Atomic Habits",
                        "content": "James Clear introduces the concept of atomic habits - small changes that seem insignificant at first but compound into remarkable results over time. A 1% improvement may not seem like much, but if you get 1% better each day for a year, you'll end up 37 times better. Conversely, if you get 1% worse each day, you'll decline nearly down to zero. The problem is that we often expect linear progress when reality is more like compound interest. Small changes often appear to make no difference until you cross a critical threshold. Clear explains that habits are the compound interest of self-improvement. The same forces that make bad habits easy to form also make good habits easy to form. The key is understanding how habits work and how to design systems that make good habits inevitable and bad habits impossible. This book provides a practical framework for building better habits and breaking bad ones, based on the latest research in psychology, neuroscience, and behavioral science.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_1.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 2,
                        "title": "The Four Laws of Behavior Change",
                        "content": "Clear presents a simple framework for building good habits and breaking bad ones, based on four laws. The 1st Law (Make it Obvious): Make your habits obvious by using implementation intentions ('I will [BEHAVIOR] at [TIME] in [LOCATION]') and habit stacking ('After [CURRENT HABIT], I will [NEW HABIT]'). The 2nd Law (Make it Attractive): Make your habits attractive by using temptation bundling (pairing something you want to do with something you need to do) and joining groups where your desired behavior is the normal behavior. The 3rd Law (Make it Easy): Make your habits easy by reducing friction, using the two-minute rule (make habits so easy you can't say no), and automating your habits. The 4th Law (Make it Satisfying): Make your habits satisfying by using immediate rewards and tracking your progress. To break bad habits, invert these laws: make them invisible, unattractive, difficult, and unsatisfying. The key insight is that you don't rise to the level of your goals; you fall to the level of your systems. Focus on building better systems rather than setting better goals.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_2.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 3,
                        "title": "Advanced Tactics: From Habits to Identity",
                        "content": "Clear explains that the most effective way to change your habits is to focus not on what you want to achieve, but on who you wish to become. Every action is a vote for the type of person you wish to become. The goal is not to read a book, but to become a reader. The goal is not to run a marathon, but to become a runner. Identity change is the North Star of habit change. However, you can't become someone new overnight. You need to prove your new identity to yourself with small wins. Clear also discusses the importance of finding the right environment, as environment is the invisible hand that shapes human behavior. Small changes in context can lead to large changes in behavior over time. He emphasizes the importance of the Goldilocks Rule - maintaining motivation by working on tasks that are right on the edge of your current abilities. Finally, he addresses how to get back on track when you break a habit, emphasizing that missing once is an accident, but missing twice is the start of a new habit. The key is to never miss twice and to be patient - results take time, but they will come if you stick with the process.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_3.mp3"
                    }
                ])
            elif book_obj.title == "Clean Code":
                content_sections_data.extend([
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 1,
                        "title": "Introduction: What is Clean Code?",
                        "content": "Robert C. Martin, also known as Uncle Bob, introduces the concept of clean code and why it matters. Clean code is code that is easy to understand, easy to modify, and easy to test. It reads like well-written prose. Clean code is not written by following a set of rules; it's written by professionals who care about their craft. The book argues that the only way to go fast is to go well - writing clean code is not a luxury, it's a necessity. Bad code slows down development, increases bugs, and makes the codebase unmaintainable. Martin emphasizes that as professionals, we have a responsibility to write code that our colleagues can understand and maintain. The book is organized into three parts: principles, patterns, and practices of clean code. It covers topics from meaningful names and functions to error handling and concurrency. The goal is to help developers write code that not only works but is also maintainable, readable, and professional.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_1.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 2,
                        "title": "Core Principles: Meaningful Names, Functions, and Classes",
                        "content": "Martin provides detailed guidance on writing clean code, starting with meaningful names. Names should reveal intent, avoid disinformation, make meaningful distinctions, be pronounceable, and be searchable. Functions should be small, do one thing, have descriptive names, and have few arguments (ideally zero, one, or two). The fewer arguments a function has, the easier it is to understand and test. Functions should have no side effects and should either do something or answer something, but not both. Classes should be small, have a single responsibility, and have high cohesion. The Single Responsibility Principle states that a class should have only one reason to change. Martin also emphasizes the importance of comments - good code is self-documenting, and comments are often a sign of failure to express yourself in code. When you find yourself writing a comment, try to refactor the code so the comment becomes unnecessary. The goal is to write code that is so clear that comments are redundant.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_2.mp3"
                    },
                    {
                        "summary_id": summ_obj.id,
                        "section_order": 3,
                        "title": "Advanced Practices: Error Handling, Boundaries, and Testing",
                        "content": "Martin covers advanced topics including error handling, which should be done properly and explicitly. Use exceptions rather than return codes, write try-catch-finally statements first, provide context with exceptions, and don't return null or pass null. The book emphasizes the importance of writing clean tests using the three laws of Test-Driven Development (TDD): you may not write production code until you have written a failing unit test, you may not write more of a unit test than is sufficient to fail, and you may not write more production code than is sufficient to pass the currently failing test. Tests should be fast, independent, repeatable, self-validating, and timely. Martin also discusses how to handle boundaries with third-party code, learning tests, and using adapters to isolate boundaries. The book concludes with a comprehensive example of refactoring a program, showing how to apply all the principles discussed. The key message is that writing clean code requires discipline, practice, and a commitment to craftsmanship. It's not about following rules blindly, but about understanding the principles and applying them thoughtfully to create code that is professional, maintainable, and a joy to work with.",
                        "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_3.mp3"
                    }
                ])
        
        # Add sections for remaining approved summaries (with shorter content)
        remaining_summaries = [s for s in approved_summaries if s not in selected_summaries]
        for idx, summ_obj in enumerate(remaining_summaries[:10]):  # Add sections for first 10 remaining summaries
            content_sections_data.extend([
                {
                    "summary_id": summ_obj.id,
                    "section_order": 1,
                    "title": "Introduction",
                    "content": f"This summary provides a comprehensive overview of {summ_obj.title}...",
                    "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_1.mp3"
                },
                {
                    "summary_id": summ_obj.id,
                    "section_order": 2,
                    "title": "Key Concepts",
                    "content": f"The main concepts and ideas presented in {summ_obj.title} are...",
                    "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_2.mp3"
                },
            ])
            # Add a third section for some summaries
            if idx < 5:
                content_sections_data.append({
                    "summary_id": summ_obj.id,
                    "section_order": 3,
                    "title": "Conclusion",
                    "content": f"In conclusion, {summ_obj.title} offers valuable insights...",
                    "audio_segment_url": f"https://example.com/audio_segment_{summ_obj.id}_3.mp3"
                })
        
        for cs_data in content_sections_data:
            cs = content_section.ContentSection(**cs_data)
            db.add(cs)
        db.commit()
        print(f"✅ Created {db.query(content_section.ContentSection).count()} content sections")
        
        # 13. Comments
        print("💬 Creating Comments...")
        comments_data = []
        # Add comments for various summaries
        approved_summaries = [s for s in summaries if s.status == "approved"]
        
        # Add 2-3 comments per summary for first 10 summaries
        for idx, summ_obj in enumerate(approved_summaries[:10]):
            comments_data.extend([
                {
                    "summary_id": summ_obj.id,
                    "user_id": writer_user.id if idx % 2 == 0 else reader_user.id,
                    "content": f"Excellent summary of {summ_obj.title}! Very insightful.",
                    "parent_comment_id": None,
                    "access": CommentAccess.PUBLIC
                },
                {
                    "summary_id": summ_obj.id,
                    "user_id": reader_user.id if idx % 2 == 0 else writer_user.id,
                    "content": "This helped me understand the key concepts much better. Thank you!",
                    "parent_comment_id": None,
                    "access": CommentAccess.PUBLIC
                },
            ])
            # Add a third comment for some summaries
            if idx < 5:
                comments_data.append({
                    "summary_id": summ_obj.id,
                    "user_id": reader_user.id,
                    "content": "I highly recommend reading the full book after this summary.",
                    "parent_comment_id": None,
                    "access": CommentAccess.PUBLIC
                })
        
        for comment_data in comments_data:
            c = comment.Comment(**comment_data)
            db.add(c)
        db.commit()
        print(f"✅ Created {db.query(comment.Comment).count()} comments")
        
        # 14. Admin Comments
        print("👨‍💼 Creating Admin Comments...")
        admin_comments_data = []
        approved_summaries = [s for s in summaries if s.status == "approved"]
        
        # Add admin comments for first 8 approved summaries
        for summ_obj in approved_summaries[:8]:
            admin_comments_data.append({
                "summary_id": summ_obj.id,
                "text_content": f"Summary '{summ_obj.title}' has been reviewed and approved. High-quality content!",
                "parent_comment_id": None
            })
        
        for ac_data in admin_comments_data:
            ac = admin_comment.AdminComment(**ac_data)
            db.add(ac)
        db.commit()
        print(f"✅ Created {db.query(admin_comment.AdminComment).count()} admin comments")
        
        print("\n🎉 Data seeding completed!")
        print("\n📊 Summary:")
        print(f"  - User Roles: {db.query(user_role.UserRole).count()}")
        print(f"  - Users: {db.query(user.User).count()}")
        print(f"  - Categories: {db.query(category.Category).count()}")
        print(f"  - Authors: {db.query(author.Author).count()}")
        print(f"  - Publishers: {db.query(publisher.Publisher).count()}")
        print(f"  - Books: {db.query(book.Book).count()}")
        print(f"  - Carts: {db.query(cart.Cart).count()}")
        print(f"  - Cart Items: {db.query(cart_item.CartItem).count()}")
        print(f"  - Orders: {db.query(order.Order).count()}")
        print(f"  - Order Details: {db.query(order_detail.OrderDetail).count()}")
        print(f"  - Summaries: {db.query(summary.Summary).count()}")
        print(f"  - Content Sections: {db.query(content_section.ContentSection).count()}")
        print(f"  - Comments: {db.query(comment.Comment).count()}")
        print(f"  - Admin Comments: {db.query(admin_comment.AdminComment).count()}")
        print("\n🔑 Login information:")
        print("  - Admin: admin@example.com / admin123")
        print("  - User 1: writer@example.com / password123")
        print("  - User 2: reader@example.com / password123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Ensure all models are imported
    import app.models  # noqa: F401
    
    seed_data()

