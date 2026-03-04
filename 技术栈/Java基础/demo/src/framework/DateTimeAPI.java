package framework;

import java.time.*;
import java.time.format.*;
import java.time.temporal.*;
import java.util.Date;
import java.util.concurrent.TimeUnit;

/**
 * 日期时间API示例
 * 演示Java 8及以上版本的日期时间处理功能
 */
public class DateTimeAPI {
    public static void main(String[] args) throws InterruptedException {
        // 获取当前日期和时间
        System.out.println("===== 获取当前日期和时间 =====");
        LocalDate currentDate = LocalDate.now();
        System.out.println("当前日期: " + currentDate);
        
        LocalTime currentTime = LocalTime.now();
        System.out.println("当前时间: " + currentTime);
        
        LocalDateTime currentDateTime = LocalDateTime.now();
        System.out.println("当前日期时间: " + currentDateTime);
        
        // 创建特定的日期时间
        System.out.println("\n===== 创建特定的日期时间 =====");
        LocalDate birthDate = LocalDate.of(1990, 5, 15);
        System.out.println("指定日期: " + birthDate);
        
        LocalTime meetingTime = LocalTime.of(14, 30, 0);
        System.out.println("指定时间: " + meetingTime);
        
        LocalDateTime appointment = LocalDateTime.of(2024, 12, 25, 10, 0, 0);
        System.out.println("指定日期时间: " + appointment);
        
        // 日期时间格式化
        System.out.println("\n===== 日期时间格式化 =====");
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formattedDateTime = currentDateTime.format(formatter);
        System.out.println("格式化后的日期时间: " + formattedDateTime);
        
        // 解析字符串为日期时间
        String dateTimeStr = "2024-01-15 10:30:00";
        LocalDateTime parsedDateTime = LocalDateTime.parse(dateTimeStr, formatter);
        System.out.println("解析后的日期时间: " + parsedDateTime);
        
        // 日期时间计算
        System.out.println("\n===== 日期时间计算 =====");
        // 添加时间
        LocalDate tomorrow = currentDate.plusDays(1);
        System.out.println("明天: " + tomorrow);
        
        LocalDate nextWeek = currentDate.plusWeeks(1);
        System.out.println("下周: " + nextWeek);
        
        LocalDate nextMonth = currentDate.plusMonths(1);
        System.out.println("下个月: " + nextMonth);
        
        // 减少时间
        LocalDate lastYear = currentDate.minusYears(1);
        System.out.println("去年今天: " + lastYear);
        
        // 使用TemporalAdjuster
        LocalDate firstDayOfMonth = currentDate.with(TemporalAdjusters.firstDayOfMonth());
        System.out.println("本月第一天: " + firstDayOfMonth);
        
        LocalDate lastDayOfMonth = currentDate.with(TemporalAdjusters.lastDayOfMonth());
        System.out.println("本月最后一天: " + lastDayOfMonth);
        
        // 计算两个日期之间的天数
        long daysBetween = ChronoUnit.DAYS.between(birthDate, currentDate);
        System.out.println("从" + birthDate + "到" + currentDate + "共有" + daysBetween + "天");
        
        // 时间段
        System.out.println("\n===== 时间段 =====");
        // 计算时间差
        LocalTime startTime = LocalTime.of(9, 0, 0);
        LocalTime endTime = LocalTime.of(18, 30, 0);
        Duration duration = Duration.between(startTime, endTime);
        System.out.println("工作时长: " + duration.toHours() + "小时" + duration.toMinutesPart() + "分钟");
        
        // 日期区间
        Period period = Period.between(birthDate, currentDate);
        System.out.println("年龄: " + period.getYears() + "岁" + period.getMonths() + "个月" + period.getDays() + "天");
        
        // 时区处理
        System.out.println("\n===== 时区处理 =====");
        ZonedDateTime beijingTime = ZonedDateTime.now(ZoneId.of("Asia/Shanghai"));
        System.out.println("北京时区时间: " + beijingTime);
        
        ZonedDateTime newYorkTime = ZonedDateTime.now(ZoneId.of("America/New_York"));
        System.out.println("纽约时区时间: " + newYorkTime);
        
        // 时区转换
        ZonedDateTime convertedTime = beijingTime.withZoneSameInstant(ZoneId.of("America/Los_Angeles"));
        System.out.println("北京时区时间转换为洛杉矶时间: " + convertedTime);
        
        // 与旧版Date的互转
        System.out.println("\n===== 与旧版Date互转 =====");
        // Date转LocalDateTime
        Date oldDate = new Date();
        Instant instant = oldDate.toInstant();
        LocalDateTime dateToLocalDateTime = instant.atZone(ZoneId.systemDefault()).toLocalDateTime();
        System.out.println("Date转LocalDateTime: " + dateToLocalDateTime);
        
        // LocalDateTime转Date
        Instant instant2 = currentDateTime.atZone(ZoneId.systemDefault()).toInstant();
        Date localDateTimeToDate = Date.from(instant2);
        System.out.println("LocalDateTime转Date: " + localDateTimeToDate);
        
        // 实际应用示例 - 倒计时
        System.out.println("\n===== 实际应用示例 - 倒计时 =====");
        LocalDateTime futureDateTime = LocalDateTime.now().plusSeconds(5);
        System.out.println("开始倒计时，5秒后结束...");
        
        while (LocalDateTime.now().isBefore(futureDateTime)) {
            LocalDateTime now = LocalDateTime.now();
            Duration remaining = Duration.between(now, futureDateTime);
            System.out.print("剩余: " + remaining.getSeconds() + "秒\r");
            Thread.sleep(1000);
        }
        System.out.println("倒计时结束!           ");
        
        // 日期比较
        System.out.println("\n===== 日期比较 =====");
        LocalDate date1 = LocalDate.of(2024, 1, 1);
        LocalDate date2 = LocalDate.of(2024, 12, 31);
        
        System.out.println(date1 + " 在 " + date2 + " 之前? " + date1.isBefore(date2));
        System.out.println(date1 + " 在 " + date2 + " 之后? " + date1.isAfter(date2));
        System.out.println(date1 + " 是否等于 " + date1 + "? " + date1.isEqual(date1));
        
        // 检查闰年
        System.out.println("\n===== 检查闰年 =====");
        System.out.println("2024年是闰年? " + Year.of(2024).isLeap());
        System.out.println("2023年是闰年? " + Year.of(2023).isLeap());
    }
}