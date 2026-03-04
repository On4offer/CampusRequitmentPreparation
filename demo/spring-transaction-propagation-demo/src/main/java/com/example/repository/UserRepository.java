package com.example.repository;

import com.example.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    @Modifying
    @Query(value = "UPDATE t_user SET balance = balance - :amount WHERE id = :userId AND balance >= :amount", nativeQuery = true)
    int decreaseBalance(@Param("userId") Long userId, @Param("amount") BigDecimal amount);
}
