# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [ ] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [ ] Backup cũng phải ở trong lãnh thổ VN
- [ ] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [ ] Thu thập consent trước khi dùng data cho AI training
- [ ] Có mechanism để user rút consent (Right to Erasure)
- [ ] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [ ] Có incident response plan
- [ ] Alert tự động khi phát hiện breach
- [ ] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [ ] Đã bổ nhiệm Data Protection Officer
- [ ] DPO có thể liên hệ tại: Cần MedViet bổ nhiệm người phụ trách và cung cấp email/điện thoại chính thức

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) | ✅ Done | Platform Team |
| Encryption | AES-256 at rest, TLS 1.3 in transit | 🚧 In Progress | Infra Team |
| Audit logging | CloudTrail + API access logs | ⬜ Todo | Platform Team |
| Breach detection | Anomaly monitoring (Prometheus) | ⬜ Todo | Security Team |

## F. TODO: Điền vào phần còn thiếu
- Audit logging: log mọi request API vào hệ thống tập trung với `user_id`, role, endpoint, action, resource, status code, request id, source IP, timestamp, và decision RBAC/OPA. Log phải immutable bằng WORM/S3 Object Lock hoặc dịch vụ tương đương, retention tối thiểu theo policy nội bộ, có dashboard truy vấn cho DPO/Security.
- Breach detection: triển khai Prometheus metrics cho API lỗi 401/403 bất thường, volume export dữ liệu, truy cập ngoài giờ, và số lượng record trả về; Grafana alert gửi đến kênh incident response. Bổ sung rule phát hiện truy cập raw PII bởi non-admin, nhiều lần decrypt thất bại, và export restricted data ra ngoài VN.
- Encryption: hoàn tất quản lý key bằng KMS/HSM thay cho file `.vault_key`, bật key rotation định kỳ, phân quyền decrypt theo service account, và audit mọi thao tác decrypt.
