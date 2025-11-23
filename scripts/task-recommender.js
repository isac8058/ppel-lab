#!/usr/bin/env node

/**
 * PPEL Lab Website - Daily Task Recommender
 *
 * This script analyzes the codebase and generates task recommendations
 * based on code quality, performance, and feature completeness.
 */

const fs = require('fs');
const path = require('path');

class TaskRecommender {
    constructor() {
        this.tasks = [];
        this.projectRoot = path.join(__dirname, '..');
    }

    // Analyze the codebase
    async analyze() {
        console.log('🔍 Analyzing PPEL Lab codebase...\n');

        await this.checkImageOptimization();
        await this.checkAccessibility();
        await this.checkPerformance();
        await this.checkSEO();
        await this.checkCodeQuality();
        await this.checkFeatures();
        await this.checkSecurity();

        return this.tasks;
    }

    // Check for image optimization opportunities
    async checkImageOptimization() {
        const imageDir = path.join(this.projectRoot, 'image');

        if (fs.existsSync(imageDir)) {
            const images = this.getAllFiles(imageDir).filter(f =>
                /\.(jpg|jpeg|png|gif)$/i.test(f)
            );

            let largeImages = [];
            for (const img of images) {
                const stats = fs.statSync(img);
                const sizeKB = stats.size / 1024;
                if (sizeKB > 200) {
                    largeImages.push({ path: img, size: sizeKB });
                }
            }

            if (largeImages.length > 0) {
                this.tasks.push({
                    priority: 'high',
                    category: '이미지 최적화',
                    title: `${largeImages.length}개 이미지 압축 필요`,
                    description: `200KB 초과 이미지 발견. WebP 변환 및 압축 권장.`,
                    files: largeImages.slice(0, 3).map(i => path.basename(i.path)),
                    effort: 'low'
                });
            }

            // Check for WebP support
            const hasWebP = images.some(f => f.endsWith('.webp'));
            if (!hasWebP && images.length > 0) {
                this.tasks.push({
                    priority: 'medium',
                    category: '이미지 최적화',
                    title: 'WebP 이미지 포맷 도입',
                    description: '최신 WebP 포맷으로 변환하여 로딩 속도 개선',
                    effort: 'medium'
                });
            }
        }
    }

    // Check accessibility issues
    async checkAccessibility() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for alt tags
            const imgWithoutAlt = (content.match(/<img(?![^>]*alt=)[^>]*>/gi) || []).length;
            if (imgWithoutAlt > 0) {
                this.tasks.push({
                    priority: 'high',
                    category: '접근성',
                    title: `이미지 alt 속성 추가 (${imgWithoutAlt}개)`,
                    description: '스크린 리더 지원을 위해 모든 이미지에 alt 속성 필요',
                    effort: 'low'
                });
            }

            // Check for ARIA labels
            const hasAriaLabels = content.includes('aria-label');
            if (!hasAriaLabels) {
                this.tasks.push({
                    priority: 'medium',
                    category: '접근성',
                    title: 'ARIA 레이블 추가',
                    description: '인터랙티브 요소에 ARIA 레이블 추가하여 접근성 향상',
                    effort: 'medium'
                });
            }

            // Check for skip link
            const hasSkipLink = content.includes('skip-to-content') || content.includes('skip-link');
            if (!hasSkipLink) {
                this.tasks.push({
                    priority: 'low',
                    category: '접근성',
                    title: 'Skip Navigation 링크 추가',
                    description: '키보드 사용자를 위한 본문 바로가기 링크',
                    effort: 'low'
                });
            }
        }
    }

    // Check performance issues
    async checkPerformance() {
        const cssFile = path.join(this.projectRoot, 'styles.css');
        const jsFile = path.join(this.projectRoot, 'script.js');

        // Check CSS file size
        if (fs.existsSync(cssFile)) {
            const stats = fs.statSync(cssFile);
            const sizeKB = stats.size / 1024;
            if (sizeKB > 50) {
                this.tasks.push({
                    priority: 'medium',
                    category: '성능',
                    title: 'CSS 파일 최소화',
                    description: `CSS 파일 ${sizeKB.toFixed(1)}KB - 미니파이 및 미사용 스타일 제거 권장`,
                    effort: 'medium'
                });
            }
        }

        // Check JS file size
        if (fs.existsSync(jsFile)) {
            const stats = fs.statSync(jsFile);
            const sizeKB = stats.size / 1024;
            if (sizeKB > 30) {
                this.tasks.push({
                    priority: 'medium',
                    category: '성능',
                    title: 'JavaScript 파일 최소화',
                    description: `JS 파일 ${sizeKB.toFixed(1)}KB - 미니파이 권장`,
                    effort: 'low'
                });
            }
        }

        // Check for lazy loading
        const htmlFile = path.join(this.projectRoot, 'index.html');
        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');
            const hasLazyLoading = content.includes('loading="lazy"');
            if (!hasLazyLoading) {
                this.tasks.push({
                    priority: 'high',
                    category: '성능',
                    title: '이미지 Lazy Loading 적용',
                    description: '스크롤 시 이미지 로딩으로 초기 로딩 속도 개선',
                    effort: 'low'
                });
            }
        }
    }

    // Check SEO improvements
    async checkSEO() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for sitemap
            const sitemapFile = path.join(this.projectRoot, 'sitemap.xml');
            if (!fs.existsSync(sitemapFile)) {
                this.tasks.push({
                    priority: 'medium',
                    category: 'SEO',
                    title: 'Sitemap.xml 생성',
                    description: '검색 엔진 인덱싱을 위한 사이트맵 생성',
                    effort: 'low'
                });
            }

            // Check for robots.txt
            const robotsFile = path.join(this.projectRoot, 'robots.txt');
            if (!fs.existsSync(robotsFile)) {
                this.tasks.push({
                    priority: 'medium',
                    category: 'SEO',
                    title: 'robots.txt 생성',
                    description: '검색 엔진 크롤링 지침 파일 생성',
                    effort: 'low'
                });
            }

            // Check for structured data
            const hasStructuredData = content.includes('application/ld+json');
            if (!hasStructuredData) {
                this.tasks.push({
                    priority: 'medium',
                    category: 'SEO',
                    title: 'Schema.org 구조화 데이터 추가',
                    description: '검색 결과에서 풍부한 스니펫 표시를 위한 구조화 데이터',
                    effort: 'medium'
                });
            }
        }
    }

    // Check code quality
    async checkCodeQuality() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for inline styles
            const inlineStyles = (content.match(/style="[^"]+"/g) || []).length;
            if (inlineStyles > 20) {
                this.tasks.push({
                    priority: 'low',
                    category: '코드 품질',
                    title: `인라인 스타일 정리 (${inlineStyles}개)`,
                    description: '인라인 스타일을 CSS 클래스로 이동하여 유지보수성 향상',
                    effort: 'high'
                });
            }

            // Check for console.log
            const jsFile = path.join(this.projectRoot, 'script.js');
            if (fs.existsSync(jsFile)) {
                const jsContent = fs.readFileSync(jsFile, 'utf8');
                const consoleLogs = (jsContent.match(/console\.(log|warn|error)/g) || []).length;
                if (consoleLogs > 0) {
                    this.tasks.push({
                        priority: 'low',
                        category: '코드 품질',
                        title: `console.log 제거 (${consoleLogs}개)`,
                        description: '프로덕션 코드에서 디버그 로그 제거',
                        effort: 'low'
                    });
                }
            }
        }
    }

    // Check for missing features
    async checkFeatures() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for contact form
            const hasContactForm = content.includes('<form') && content.includes('submit');
            if (!hasContactForm) {
                this.tasks.push({
                    priority: 'medium',
                    category: '기능',
                    title: '연락처 폼 추가',
                    description: '이메일 팝업 대신 대학원생 문의 폼 구현',
                    effort: 'high'
                });
            }

            // Check for search functionality
            const hasSearch = content.includes('search') || content.includes('검색');
            if (!hasSearch) {
                this.tasks.push({
                    priority: 'low',
                    category: '기능',
                    title: '논문 검색 기능 추가',
                    description: '연도, 저자, 키워드별 논문 필터링 기능',
                    effort: 'high'
                });
            }

            // Check for 404 page
            const notFoundPage = path.join(this.projectRoot, '404.html');
            if (!fs.existsSync(notFoundPage)) {
                this.tasks.push({
                    priority: 'low',
                    category: '기능',
                    title: '404 에러 페이지 추가',
                    description: '사용자 친화적인 에러 페이지 생성',
                    effort: 'low'
                });
            }

            // Check for favicon
            const hasFavicon = content.includes('favicon') || content.includes('icon');
            if (!hasFavicon) {
                this.tasks.push({
                    priority: 'medium',
                    category: '기능',
                    title: 'Favicon 추가',
                    description: '브라우저 탭에 표시될 아이콘 추가',
                    effort: 'low'
                });
            }
        }
    }

    // Check security
    async checkSecurity() {
        const htmlFile = path.join(this.projectRoot, 'index.html');

        if (fs.existsSync(htmlFile)) {
            const content = fs.readFileSync(htmlFile, 'utf8');

            // Check for external links with target="_blank"
            const unsafeLinks = (content.match(/target="_blank"(?![^>]*rel=)/g) || []).length;
            if (unsafeLinks > 0) {
                this.tasks.push({
                    priority: 'medium',
                    category: '보안',
                    title: `외부 링크 보안 강화 (${unsafeLinks}개)`,
                    description: 'target="_blank" 링크에 rel="noopener noreferrer" 추가',
                    effort: 'low'
                });
            }
        }
    }

    // Helper: Get all files recursively
    getAllFiles(dirPath, arrayOfFiles = []) {
        const files = fs.readdirSync(dirPath);

        files.forEach(file => {
            const filePath = path.join(dirPath, file);
            if (fs.statSync(filePath).isDirectory()) {
                arrayOfFiles = this.getAllFiles(filePath, arrayOfFiles);
            } else {
                arrayOfFiles.push(filePath);
            }
        });

        return arrayOfFiles;
    }

    // Generate report
    generateReport() {
        const today = new Date().toISOString().split('T')[0];

        let report = `# 📋 PPEL Lab 일일 할일 보고서\n\n`;
        report += `**날짜:** ${today}\n`;
        report += `**총 추천 작업:** ${this.tasks.length}개\n\n`;

        // Group by priority
        const highPriority = this.tasks.filter(t => t.priority === 'high');
        const mediumPriority = this.tasks.filter(t => t.priority === 'medium');
        const lowPriority = this.tasks.filter(t => t.priority === 'low');

        report += `---\n\n`;

        if (highPriority.length > 0) {
            report += `## 🔴 높은 우선순위 (${highPriority.length}개)\n\n`;
            highPriority.forEach(task => {
                report += this.formatTask(task);
            });
        }

        if (mediumPriority.length > 0) {
            report += `## 🟡 중간 우선순위 (${mediumPriority.length}개)\n\n`;
            mediumPriority.forEach(task => {
                report += this.formatTask(task);
            });
        }

        if (lowPriority.length > 0) {
            report += `## 🟢 낮은 우선순위 (${lowPriority.length}개)\n\n`;
            lowPriority.forEach(task => {
                report += this.formatTask(task);
            });
        }

        report += `---\n\n`;
        report += `*이 보고서는 자동으로 생성되었습니다.*\n`;

        return report;
    }

    formatTask(task) {
        let output = `### ${task.title}\n`;
        output += `- **카테고리:** ${task.category}\n`;
        output += `- **설명:** ${task.description}\n`;
        output += `- **예상 노력:** ${task.effort === 'low' ? '낮음 ⭐' : task.effort === 'medium' ? '중간 ⭐⭐' : '높음 ⭐⭐⭐'}\n`;
        if (task.files) {
            output += `- **관련 파일:** ${task.files.join(', ')}\n`;
        }
        output += '\n';
        return output;
    }
}

// Main execution
async function main() {
    const recommender = new TaskRecommender();
    await recommender.analyze();

    const report = recommender.generateReport();

    // Output to console
    console.log(report);

    // Save to file
    const outputPath = path.join(__dirname, '..', 'DAILY_TASKS.md');
    fs.writeFileSync(outputPath, report);
    console.log(`\n✅ 보고서가 DAILY_TASKS.md에 저장되었습니다.`);

    // Return task count for GitHub Actions
    return recommender.tasks.length;
}

main().catch(console.error);
