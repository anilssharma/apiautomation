SET NOCOUNT ON;
SET XACT_ABORT ON;

BEGIN TRANSACTION;

INSERT INTO dbo.orders (order_number, user_id, created_at)
SELECT sample.order_number, sample.user_id, sample.created_at
FROM (VALUES
    (N'ORD-1001', N'USER-101', CAST(N'2026-06-01T08:55:00+00:00' AS DATETIMEOFFSET(0))),
    (N'ORD-1002', N'USER-101', CAST(N'2026-06-03T14:10:00+00:00' AS DATETIMEOFFSET(0))),
    (N'ORD-1003', N'USER-202', CAST(N'2026-06-02T11:20:00+00:00' AS DATETIMEOFFSET(0))),
    (N'ORD-1004', N'USER-303', CAST(N'2026-06-05T09:00:00+00:00' AS DATETIMEOFFSET(0)))
) AS sample(order_number, user_id, created_at)
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.orders AS existing
    WHERE existing.order_number = sample.order_number
);

INSERT INTO dbo.order_status_history (order_id, status, changed_at, note)
SELECT orders.id, sample.status, sample.changed_at, sample.note
FROM (VALUES
    (N'ORD-1001', N'PENDING', CAST(N'2026-06-01T09:00:00+00:00' AS DATETIMEOFFSET(0)), N'Order placed'),
    (N'ORD-1001', N'PROCESSING', CAST(N'2026-06-01T10:30:00+00:00' AS DATETIMEOFFSET(0)), N'Payment confirmed'),
    (N'ORD-1001', N'SHIPPED', CAST(N'2026-06-02T12:00:00+00:00' AS DATETIMEOFFSET(0)), N'Carrier pickup'),
    (N'ORD-1001', N'DELIVERED', CAST(N'2026-06-04T16:45:00+00:00' AS DATETIMEOFFSET(0)), N'Delivered to recipient'),
    (N'ORD-1002', N'PENDING', CAST(N'2026-06-03T14:10:00+00:00' AS DATETIMEOFFSET(0)), N'Order placed'),
    (N'ORD-1002', N'PROCESSING', CAST(N'2026-06-03T15:00:00+00:00' AS DATETIMEOFFSET(0)), N'Payment confirmed'),
    (N'ORD-1002', N'CANCELLED', CAST(N'2026-06-04T08:15:00+00:00' AS DATETIMEOFFSET(0)), N'Cancelled by customer'),
    (N'ORD-1003', N'PENDING', CAST(N'2026-06-02T11:25:00+00:00' AS DATETIMEOFFSET(0)), N'Order placed'),
    (N'ORD-1003', N'PROCESSING', CAST(N'2026-06-02T13:40:00+00:00' AS DATETIMEOFFSET(0)), N'Payment confirmed'),
    (N'ORD-1003', N'SHIPPED', CAST(N'2026-06-03T09:00:00+00:00' AS DATETIMEOFFSET(0)), N'Carrier pickup'),
    (N'ORD-1004', N'PENDING', CAST(N'2026-06-05T09:05:00+00:00' AS DATETIMEOFFSET(0)), N'Order placed'),
    (N'ORD-1004', N'PROCESSING', CAST(N'2026-06-05T10:00:00+00:00' AS DATETIMEOFFSET(0)), N'Payment confirmed')
) AS sample(order_number, status, changed_at, note)
INNER JOIN dbo.orders AS orders ON orders.order_number = sample.order_number
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.order_status_history AS existing
    WHERE existing.order_id = orders.id
      AND existing.changed_at = sample.changed_at
);

COMMIT TRANSACTION;