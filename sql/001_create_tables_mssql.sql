IF OBJECT_ID(N'dbo.orders', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.orders (
        id INT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_orders PRIMARY KEY,
        order_number NVARCHAR(50) NOT NULL,
        user_id NVARCHAR(100) NOT NULL,
        created_at DATETIMEOFFSET(0) NOT NULL,
        CONSTRAINT UQ_orders_order_number UNIQUE (order_number)
    );
END;
GO

IF OBJECT_ID(N'dbo.order_status_history', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.order_status_history (
        id INT IDENTITY(1, 1) NOT NULL CONSTRAINT PK_order_status_history PRIMARY KEY,
        order_id INT NOT NULL,
        status NVARCHAR(20) NOT NULL,
        changed_at DATETIMEOFFSET(0) NOT NULL,
        note NVARCHAR(500) NULL,
        CONSTRAINT FK_order_status_history_orders
            FOREIGN KEY (order_id) REFERENCES dbo.orders(id) ON DELETE CASCADE,
        CONSTRAINT CK_order_status_history_status
            CHECK (status IN (N'PENDING', N'PROCESSING', N'SHIPPED', N'DELIVERED', N'CANCELLED', N'RETURNED')),
        CONSTRAINT UQ_order_status_changed_at UNIQUE (order_id, changed_at)
    );
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_orders_user_id' AND object_id = OBJECT_ID(N'dbo.orders')
)
BEGIN
    CREATE INDEX IX_orders_user_id ON dbo.orders(user_id);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_order_status_history_order_changed'
      AND object_id = OBJECT_ID(N'dbo.order_status_history')
)
BEGIN
    CREATE INDEX IX_order_status_history_order_changed
        ON dbo.order_status_history(order_id, changed_at);
END;
GO

IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE name = N'IX_order_status_history_changed_at'
      AND object_id = OBJECT_ID(N'dbo.order_status_history')
)
BEGIN
    CREATE INDEX IX_order_status_history_changed_at
        ON dbo.order_status_history(changed_at);
END;
GO