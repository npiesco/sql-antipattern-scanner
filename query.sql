SELECT *
FROM users u, orders o, products p
WHERE u.id = o.user_id
  AND o.product_id = p.id
  AND u.name LIKE '%john%'
  AND o.status = NULL
  AND p.price BETWEEN 100 AND 500
  AND o.id IN (SELECT id FROM abandoned_orders)
  AND LOWER(p.name) IN ('widget', 'gadget', 'gizmo')
  AND u.created_at > '2022-01-01'
GROUP BY 1, 2, 3
HAVING COUNT(*) > 10
ORDER BY RAND()
LIMIT 1000;