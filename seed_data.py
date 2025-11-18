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
            {
                "title": "Yellow Flowers on the Green Grass",
                "category_id": categories[0].id,
                "author_id": authors[0].id,
                "publisher_id": publishers[0].id,
                "publish_date": date(2010, 1, 1),
                "cover_image": "https://via.placeholder.com/300x400",
                "price": Decimal("120000"),
                "stock_quantity": 50
            },
            {
                "title": "Sapiens: A Brief History of Humankind",
                "category_id": categories[1].id,
                "author_id": authors[1].id,
                "publisher_id": publishers[3].id,
                "publish_date": date(2011, 1, 1),
                "cover_image": "https://via.placeholder.com/300x400",
                "price": Decimal("250000"),
                "stock_quantity": 30
            },
            {
                "title": "How to Win Friends & Influence People",
                "category_id": categories[4].id,
                "author_id": authors[2].id,
                "publisher_id": publishers[3].id,
                "publish_date": date(1936, 1, 1),
                "cover_image": "https://via.placeholder.com/300x400",
                "price": Decimal("150000"),
                "stock_quantity": 100
            },
            {
                "title": "The Book Thief",
                "category_id": categories[0].id,
                "author_id": authors[0].id,
                "publisher_id": publishers[1].id,
                "publish_date": date(2005, 1, 1),
                "cover_image": "https://via.placeholder.com/300x400",
                "price": Decimal("180000"),
                "stock_quantity": 25
            },
        ]
        books = []
        for book_data in books_data:
            b = book.Book(**book_data)
            db.add(b)
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
        
        # 11. Summaries
        print("📄 Creating Summaries...")
        summaries_data = [
            {
                "title": "Summary: Yellow Flowers on the Green Grass",
                "book_id": books[0].id,
                "published_date": datetime.now(timezone.utc),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.5,
                "read_count": 1200,
                "audio_url": "https://example.com/audio_summary1.mp3"
            },
            {
                "title": "Summary: Sapiens - A Brief History of Humankind",
                "book_id": books[1].id,
                "published_date": datetime.now(timezone.utc),
                "user_id": writer_user.id,
                "status": "approved",
                "avg_rating": 4.8,
                "read_count": 2500,
                "audio_url": "https://example.com/audio_summary2.mp3"
            },
            {
                "title": "Summary: How to Win Friends & Influence People (Draft)",
                "book_id": books[2].id,
                "published_date": None,
                "user_id": writer_user.id,
                "status": "editing",
                "avg_rating": 0,
                "read_count": 0,
                "audio_url": None
            }
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
        content_sections_data = [
            {
                "summary_id": summaries[0].id,
                "section_order": 1,
                "title": "Introduction",
                "content": "This book describes the childhood of children in a rural Vietnamese village...",
                "audio_segment_url": "https://example.com/audio_segment1.mp3"
            },
            {
                "summary_id": summaries[0].id,
                "section_order": 2,
                "title": "Main Characters",
                "content": "The main character is Thieu, a pure-hearted boy...",
                "audio_segment_url": "https://example.com/audio_segment2.mp3"
            },
            {
                "summary_id": summaries[1].id,
                "section_order": 1,
                "title": "Overview",
                "content": "Sapiens is a book about the history of humankind from the Stone Age to modernity...",
                "audio_segment_url": "https://example.com/audio_segment3.mp3"
            },
        ]
        for cs_data in content_sections_data:
            cs = content_section.ContentSection(**cs_data)
            db.add(cs)
        db.commit()
        print(f"✅ Created {db.query(content_section.ContentSection).count()} content sections")
        
        # 13. Comments
        print("💬 Creating Comments...")
        comments_data = [
            {
                "summary_id": summaries[0].id,
                "user_id": writer_user.id,
                "content": "Excellent and detailed summary!",
                "parent_comment_id": None,
                "access": CommentAccess.PUBLIC
            },
            {
                "summary_id": summaries[0].id,
                "user_id": writer_user.id,
                "content": "Thank you for sharing!",
                "parent_comment_id": None,
                "access": CommentAccess.PUBLIC
            },
            {
                "summary_id": summaries[1].id,
                "user_id": reader_user.id,
                "content": "This book truly changed the way I view history.",
                "parent_comment_id": None,
                "access": CommentAccess.PUBLIC
            },
        ]
        for comment_data in comments_data:
            c = comment.Comment(**comment_data)
            db.add(c)
        db.commit()
        print(f"✅ Created {db.query(comment.Comment).count()} comments")
        
        # 14. Admin Comments
        print("👨‍💼 Creating Admin Comments...")
        admin_comments_data = [
            {
                "summary_id": summaries[0].id,
                "text_content": "Summary has been reviewed and published.",
                "parent_comment_id": None
            },
            {
                "summary_id": summaries[1].id,
                "text_content": "High-quality content, keep up the good work!",
                "parent_comment_id": None
            },
        ]
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
        print("  - User 1: john@example.com / password123")
        print("  - User 2: jane@example.com / password123")
        
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

