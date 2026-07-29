from app.database import engine, Base, SessionLocal
from app.domain.tenant import Tenant
from app.domain.user import User, Role

def seed_db():
    """
    Creates all SQLite tables and seeds initial mock Tenants and Users
    with appropriate roles for testing.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Tenant).count() > 0:
            return

        print("Seeding database with mock Tenants and Users...")
        
        # 1. Add Tenants with static UUIDs for easy frontend integration
        tenant_cuc = Tenant(
            id="t1111111-1111-1111-1111-111111111111", 
            ten_co_quan="Cục Cảnh sát PCCC và CNCH", 
            ma_tenant="PCCC_CUC"
        )
        tenant_hn = Tenant(
            id="t2222222-2222-2222-2222-222222222222", 
            ten_co_quan="Phòng Cảnh sát PCCC TP. Hà Nội", 
            ma_tenant="PCCC_HN"
        )
        tenant_hcm = Tenant(
            id="t3333333-3333-3333-3333-333333333333", 
            ten_co_quan="Phòng Cảnh sát PCCC TP. HCM", 
            ma_tenant="PCCC_HCM"
        )
        
        db.add_all([tenant_cuc, tenant_hn, tenant_hcm])
        db.commit()

        # 2. Add Users with different Roles for authorization testing
        users = [
            # Cục PCCC (Tenant 1)
            User(
                id="u1111111-1111-1111-1111-111111111111", 
                ho_ten="Nguyễn Văn A (Cục - Admin)", 
                vai_tro=Role.ADMIN, 
                tenant_id=tenant_cuc.id
            ),
            User(
                id="u1111111-2222-1111-1111-111111111111", 
                ho_ten="Trần Thị B (Cục - Thẩm tra viên)", 
                vai_tro=Role.THAM_TRA_VIEN, 
                tenant_id=tenant_cuc.id
            ),
            User(
                id="u1111111-3333-1111-1111-111111111111", 
                ho_ten="Lê Văn C (Cục - Phê duyệt)", 
                vai_tro=Role.CHUYEN_GIA_PHE_DUYET, 
                tenant_id=tenant_cuc.id
            ),
            
            # Phòng PCCC Hà Nội (Tenant 2)
            User(
                id="u2222222-1111-2222-2222-222222222222", 
                ho_ten="Phạm Văn D (Hà Nội - Admin)", 
                vai_tro=Role.ADMIN, 
                tenant_id=tenant_hn.id
            ),
            User(
                id="u2222222-2222-2222-2222-222222222222", 
                ho_ten="Hoàng Thị E (Hà Nội - Thẩm tra)", 
                vai_tro=Role.THAM_TRA_VIEN, 
                tenant_id=tenant_hn.id
            ),
            
            # Phòng PCCC HCM (Tenant 3)
            User(
                id="u3333333-1111-3333-3333-333333333333", 
                ho_ten="Ngô Văn F (TP.HCM - Phê duyệt)", 
                vai_tro=Role.CHUYEN_GIA_PHE_DUYET, 
                tenant_id=tenant_hcm.id
            ),
        ]
        
        db.add_all(users)
        db.commit()
        print("Database seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"Failed to seed database: {e}")
    finally:
        db.close()
