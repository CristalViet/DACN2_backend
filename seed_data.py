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
        
        for idx, summ_obj in enumerate(approved_summaries[:15]):  # Add sections for first 15 approved summaries
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
            if idx < 10:
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

