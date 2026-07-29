# Project Plan: Multi-Tenant Document Catalog & Upload System (PCCC)

This document contains the implementation blueprint and task checklist for UC-A0-01 (Document Catalog Management) and UC-A0-02 (Upload / Replace Source Document), based on the [class_diagram_A0-01_A0-02.puml](file:///C:/Users/huutu/Nextcloud/Desktop/PCCC/class_diagram_A0-01_A0-02.puml) design.

---

## 1. Mappings: Java Design to FastAPI / Python

We will translate the design patterns described in the class diagram into Pythonic equivalents:

| UML Design Pattern | Java/UML Specifics | Python/FastAPI Equivalents |
| :--- | :--- | :--- |
| **Multi-Tenant Context** | `TenantContext` Singleton + `ThreadLocal<Tenant>` | `contextvars.ContextVar[Tenant]` for thread/async-safe request state. Set by middleware. |
| **Persistence** | `DocumentRepositoryImpl` using standard SQL `DataSource` | `SQLAlchemy` ORM scoping queries automatically to `TenantContext.getCurrentTenant().id`. |
| **Validation Chain** | `IUploadValidator` Chain of Responsibility | Linked list or list of validator classes (`PdfFormatValidator`, `DuplicateCodeValidator`) executed in sequence. |
| **File Storage** | `IFileStorageStrategy` (Strategy) & `FileStorageFactory` | `LocalStorageStrategy` & S3 Mock. Storage factory returns strategy based on tenant settings. |
| **Audit Logging** | `ChangeLogPublisher` (Observer pattern) | Publisher class notifying list of observers on DB changes (saves log events). |

---

## 2. Recommended Directory Structure

```
PCCC/
├── main.py                          # FastAPI App & routing entrypoint
├── data.db                          # Persistent SQLite database file
├── project_plan.md                  # This project plan
├── class_diagram_A0-01_A0-02.puml   # Provided design class diagram
├── templates/
│   └── index.html                   # Rich frontend dashboard (Catalog, Upload, Audit Logs)
└── app/
    ├── __init__.py
    ├── config.py                    # App configuration
    ├── database.py                  # SQLAlchemy engine & session configurations
    ├── domain/                      # Domain definitions
    │   ├── __init__.py
    │   ├── tenant.py                # Tenant model
    │   ├── user.py                  # User/Role model & role enums
    │   └── document.py              # RegulatoryDocument & DocumentStatus
    ├── core/                        # Context & Permissions
    │   ├── __init__.py
    │   ├── tenant_context.py        # TenantContext implementation
    │   └── security.py              # AccessControlService
    ├── persistence/                 # Repositories
    │   ├── __init__.py
    │   ├── repository_interface.py  # Abstract Repository base
    │   └── document_repository.py   # SQLAlchemy Repository implementation
    ├── infrastructure/              # Pattern implementers (Validators, Observers, Storage)
    │   ├── __init__.py
    │   ├── storage/                 # Storage Strategies
    │   │   ├── interface.py
    │   │   ├── local_storage.py
    │   │   └── storage_factory.py
    │   ├── validation/              # Upload Validation Chains
    │   │   ├── interface.py
    │   │   ├── pdf_validator.py
    │   │   └── code_validator.py
    │   └── audit/                   # Pub/Sub Change Log Observers
    │       ├── publisher.py
    │       ├── observer.py
    │       └── event.py
    └── services/                    # App Services (Use-cases)
        ├── __init__.py
        ├── catalog_service.py       # DocumentCatalogService implementation
        └── upload_service.py        # DocumentUploadService implementation
```

---

## 3. Database Schema

The database will be backed by **SQLite** using SQLAlchemy. The tables will include:
1. `tenants`: Stores mock tenant details (`id`, `ten_co_quan`, `ma_tenant`).
2. `users`: Stores mock user details (`id`, `ho_ten`, `vai_tro`, `tenant_id`).
3. `regulatory_documents`: Scoped by `tenant_id` (`id`, `ma_hieu`, `ten_day_du`, `co_quan_ban_hanh`, `ngay_ban_hanh`, `ngay_hieu_luc`, `trang_thai`, `file_url`, `file_checksum`, `tenant_id`, `version`).
4. `changelogs`: Audited changes (`id`, `document_id`, `action`, `performed_by`, `performed_at`, `detail`).

---

## 4. Implementation Phasing & Checklist

### Phase 1: Models & Core Setup
- [x] Create domain database configurations and model declarations (`app/domain`).
- [x] Implement `TenantContext` using Python's `contextvars`.
- [x] Seed SQLite database with mock tenants and users for development/testing.
- [x] Add FastAPI middleware to parse headers (`X-Tenant-ID`, `X-User-ID`) to populate the context.

### Phase 2: Design Patterns
- [x] Create storage interface & factory, supporting local directory output per tenant (`stored_files/{tenant_id}/`).
- [x] Create base validator interface and instantiate the Chain of Responsibility (`PdfFormatValidator` & `DuplicateCodeValidator`).
- [x] Implement the Observer pattern for Auditing, logging changes to `changelogs` table.

### Phase 3: Services & Repositories
- [x] Create `DocumentRepositoryImpl` that filters queries according to active `TenantContext`.
- [x] Implement `AccessControlService` ensuring the user has permissions (`THAM_TRA_VIEN`, `CHUYEN_GIA_PHE_DUYET`, `ADMIN`).
- [x] Add `DocumentCatalogService` and `DocumentUploadService` handling core business logic.

### Phase 4: API Connection
- [x] Implement routing controllers for:
  - `GET /api/documents` (lists/filters)
  - `POST /api/documents/upload` (submits metadata and files)
  - `PUT /api/documents/{id}/replace` (replaces files)
  - `GET /api/audit-logs` (retrieves changelogs)
  - `GET /api/tenants` and `GET /api/users` (facilitates simulated workspace switches on the frontend)
- [x] Connect routers inside [main.py](file:///C:/Users/huutu/Nextcloud/Desktop/PCCC/main.py).

### Phase 5: Client-Side Dashboard Update
- [x] Update frontend SPA (`templates/index.html`) with interactive features:
  - Role/Tenant selector dashboard.
  - Document catalog list showing status and details.
  - Interactive upload and replacement forms.
  - Live audits list.
