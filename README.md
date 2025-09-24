# AI for Life - Frontend

Ứng dụng frontend được xây dựng với React 19 và các công nghệ hiện đại, sử dụng kiến trúc feature-first và component-driven development.

## 🚀 Công nghệ sử dụng

### Core Framework & Build Tools

- **React 19** - UI framework với các tính năng mới nhất
- **Vite 7** - Build tool nhanh với HMR
- **React Router v7** - Routing với lazy loading và code splitting
- **TanStack React Query v5** - Data fetching, caching và synchronization

### Styling & UI

- **Tailwind CSS 3** - Utility-first CSS framework
- **PostCSS 8** - CSS processing với Autoprefixer

### Development & Testing

- **Storybook 9** - Component documentation và isolated development
- **Vitest 3** - Testing framework với browser testing
- **Playwright** - End-to-end testing automation
- **ESLint 9** - Code linting với flat config

### Code Quality

- **PropTypes** - Runtime type checking
- **ESLint plugins** - React Hooks, React Refresh, Storybook

## 📁 Cấu trúc thư mục

```
ai-for-life-fe/
├── .storybook/          # Cấu hình Storybook (UI docs & testing)
├── public/              # Tài nguyên tĩnh (favicon, images...)
├── src/
│   ├── app/            # Khung ứng dụng chính
│   │   ├── index.jsx          # App component chính
│   │   ├── app-provider.jsx   # Global providers (React Query, Theme...)
│   │   └── router.js          # Cấu hình routing với lazy loading
│   ├── features/       # Các tính năng theo domain (auth, dashboard...)
│   ├── lib/           # Cấu hình thư viện bên thứ ba
│   │   └── react-query.js     # Setup QueryClient
│   ├── hooks/         # Custom hooks dùng chung
│   ├── utils/         # Hàm tiện ích (cn, helpers...)
│   ├── types/         # Type definitions (JSDoc/TypeScript)
│   ├── stories/       # Storybook examples và UI components
│   ├── main.jsx       # Entry point của ứng dụng
│   └── index.css      # Global styles và Tailwind directives
├── index.html          # HTML shell
├── package.json        # Dependencies và scripts
├── vite.config.js     # Vite configuration với alias @
├── tailwind.config.js # Tailwind CSS configuration
├── postcss.config.js  # PostCSS configuration
├── eslint.config.js   # ESLint flat configuration
├── vitest.config.js   # Vitest configuration với Storybook integration
└── README.md          # Tài liệu dự án
```

## 🎯 Ý nghĩa tổ chức

### Kiến trúc Feature-First

- **`src/app/`** - Quản lý cross-cutting concerns (routing, providers)
- **`src/features/`** - Mỗi feature tự chứa components, hooks, services, tests
- **`src/lib/`** - Cấu hình và adapter cho thư viện bên thứ ba
- **`src/utils/`** - Logic dùng lại được, không phụ thuộc React

### Tối ưu hiệu năng

- **Lazy routing** - Code splitting tự động theo route
- **Alias `@`** - Import paths ngắn gọn, tránh relative path phức tạp
- **React Query** - Caching thông minh, optimistic updates

### Chất lượng phát triển

- **Storybook** - Component isolation, visual testing, documentation
- **ESLint** - Code consistency, early error detection
- **Vitest + Playwright** - Unit tests và browser testing

## 🛠️ Cài đặt và chạy

### Yêu cầu hệ thống

- Node.js >= 18
- npm hoặc yarn

### Cài đặt dependencies

```bash
# Clone repository
git clone <repository-url>
cd ai-for-life-fe

# Cài đặt packages
npm install
# hoặc
npm ci  # (khuyến nghị cho production)
```

### Development

```bash
# Chạy development server
npm run dev
# Ứng dụng sẽ chạy tại http://localhost:5173

# Chạy Storybook (component documentation)
npm run storybook
# Storybook sẽ chạy tại http://localhost:6006
```

### Build & Preview

```bash
# Build cho production
npm run build

# Preview build locally
npm run preview
# Preview sẽ chạy tại http://localhost:4173
```

### Testing & Quality

```bash
# Chạy ESLint
npm run lint

# Build Storybook static
npm run build-storybook

# Chạy tests (cần thêm script "test": "vitest")
npx vitest
```

## 🔧 Cấu hình quan trọng

### Alias Import

Dự án sử dụng alias `@` trỏ tới `src/`:

```javascript
// Thay vì
import Component from "../../../components/Component";

// Sử dụng
import Component from "@/components/Component";
```

### Lazy Loading Routes

Routes được load động để tối ưu bundle size:

```javascript
{
  path: "/login",
  lazy: async () => {
    const { LoginRoute } = await import("@/features/auth/routes/login.jsx");
    return LoginRoute;
  },
}
```

## 🚨 Lưu ý hiện tại

- **Route thiếu file**: `src/app/router.js` đang import `@/app/routes/app/public/login.jsx` nhưng file này chưa tồn tại
- **Storybook setup**: Cần kiểm tra `.storybook/main.js`, `preview.js`, `vitest.setup.js`
- **Feature structure**: Thư mục `src/features/` chưa có nội dung, cần tổ chức theo domain

## 📚 Scripts có sẵn

| Script                    | Mô tả                           |
| ------------------------- | ------------------------------- |
| `npm run dev`             | Chạy development server với HMR |
| `npm run build`           | Build production bundle         |
| `npm run preview`         | Preview production build        |
| `npm run lint`            | Chạy ESLint kiểm tra code       |
| `npm run storybook`       | Chạy Storybook development      |
| `npm run build-storybook` | Build Storybook static          |

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

## 📄 License

[Thêm thông tin license nếu có]
