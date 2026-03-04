package com.example.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import jakarta.persistence.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@NoArgsConstructor
@Entity
@Table(name = "t_order")
public class Order {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "order_no", nullable = false, unique = true)
    private String orderNo;
    
    @Column(name = "user_id", nullable = false)
    private Long userId;
    
    @Column(name = "product_id", nullable = false)
    private Long productId;
    
    @Column(nullable = false)
    private Integer quantity;
    
    @Column(name = "total_amount", nullable = false)
    private BigDecimal totalAmount;
    
    @Column(nullable = false)
    private String status; // PENDING, PAID, CANCELLED
    
    @Column(name = "create_time", nullable = false, updatable = false)
    private LocalDateTime createTime;
    
    @Column(name = "update_time", nullable = false)
    private LocalDateTime updateTime;
    
    /**
     * 实体持久化前的回调方法，用于设置创建时间和更新时间
     *
     * 此方法在实体首次保存到数据库之前自动调用，通过JPA的@PrePersist注解触发。
     * 它会将createTime和updateTime字段都设置为当前时间戳。
     */
    @PrePersist
    protected void onCreate() {
        // 设置实体的创建时间和更新时间
        createTime = LocalDateTime.now();
        updateTime = LocalDateTime.now();
    }

    
    @PreUpdate
    protected void onUpdate() {
        updateTime = LocalDateTime.now();
    }
}
