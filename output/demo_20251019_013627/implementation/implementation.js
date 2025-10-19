plaintext
# File: package.json
{
  "name": "vite-react-ts-todo",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "typecheck": "tsc -b --pretty"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.10",
    "@types/react-dom": "^18.3.2",
    "typescript": "^5.6.3",
    "vite": "^5.4.9",
    "@vitejs/plugin-react": "^4.3.3"
  }
}

# File: tsconfig.json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "Bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "types": ["vite/client"]
  },
  "include": ["src"]
}

# File: vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true
  },
  preview: {
    port: 5173,
    strictPort: true
  }
});

# File: index.html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta
      name="viewport"
      content="width=device-width, initial-scale=1, viewport-fit=cover"
    />
    <meta name="color-scheme" content="light dark" />
    <title>Todo App - React + TypeScript + Vite</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

# File: src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

const rootEl = document.getElementById('root');
if (!rootEl) {
  // If root element missing, fail fast with helpful message.
  throw new Error('Root element with id="root" not found in index.html');
}

ReactDOM.createRoot(rootEl).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

# File: src/App.tsx
import React from 'react';
import { useTodos } from './hooks/useTodos';
import { TodoInput } from './components/TodoInput';
import { TodoList } from './components/TodoList';
import { ErrorBanner } from './components/ErrorBanner';

export default function App(): JSX.Element {
  const {
    todos,
    addTodo,
    toggleTodo,
    deleteTodo,
    error,
    clearError
  } = useTodos();

  const remaining = todos.filter(t => !t.completed).length;
  const completed = todos.length - remaining;

  return (
    <div className="container">
      <header className="header">
        <h1>Todos</h1>
        <p className="subtitle" aria-live="polite">
          {todos.length === 0
            ? 'No todos yet. Add your first one below.'
            : `${remaining} remaining • ${completed} completed`}
        </p>
      </header>

      {error && (
        <ErrorBanner message={error} onClose={clearError} />
      )}

      <main>
        <section aria-labelledby="add-todo-section">
          <h2 id="add-todo-section" className="sr-only">Add todo</h2>
          <TodoInput onAdd={addTodo} />
        </section>

        <section aria-labelledby="list-todo-section" className="list-section">
          <h2 id="list-todo-section" className="sr-only">Todo list</h2>
          <TodoList
            todos={todos}
            onToggle={toggleTodo}
            onDelete={deleteTodo}
          />
        </section>
      </main>

      <footer className="footer">
        <small>Built with React, TypeScript, and Vite.</small>
      </footer>
    </div>
  );
}

# File: src/types/todo.ts
/**
 * Domain model for a Todo item.
 */
export interface Todo {
  id: string;
  title: string;
  completed: boolean;
  createdAt: number; // epoch millis
}

# File: src/utils/id.ts
/**
 * Generates a stable unique identifier string.
 * Uses crypto.randomUUID when available, falls back to time+random.
 */
export function generateId(): string {
  try {
    if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
      return crypto.randomUUID();
    }
  } catch {
    // ignore and fall back
  }
  // Fallback: time and random, base36, with a prefix for easier debugging
  return `t_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 10)}`;
}

# File: src/utils/storage.ts
import type { Todo } from '../types/todo';

const STORAGE_KEY = 'todo-app:v1:todos';

/**
 * Checks if localStorage is accessible and writeable.
 */
function storageAvailable(): boolean {
  try {
    const testKey = '__storage_test__';
    localStorage.setItem(testKey, '1');
    localStorage.removeItem(testKey);
    return true;
  } catch {
    return false;
  }
}

/**
 * Load todos from localStorage with robust error handling.
 * Returns todos and an optional error message for UI display.
 */
export function loadTodos(): { todos: Todo[]; error: string | null } {
  if (!storageAvailable()) {
    return { todos: [], error: 'Local storage is not available. Changes will not persist.' };
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { todos: [], error: null };
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) {
      return { todos: [], error: 'Corrupted saved data detected. Starting fresh.' };
    }
    // Basic shape validation; discard invalid items gracefully.
    const todos: Todo[] = parsed
      .map((item) => {
        if (
          item &&
          typeof item === 'object' &&
          typeof (item as any).id === 'string' &&
          typeof (item as any).title === 'string' &&
          typeof (item as any).completed === 'boolean' &&
          typeof (item as any).createdAt === 'number'
        ) {
          return {
            id: (item as any).id,
            title: (item as any).title,
            completed: (item as any).completed,
            createdAt: (item as any).createdAt
          } as Todo;
        }
        return null;
      })
      .filter(Boolean) as Todo[];
    return { todos, error: null };
  } catch {
    return { todos: [], error: 'Failed to read saved data. Starting with an empty list.' };
  }
}

/**
 * Save todos to localStorage.
 * Throws an Error when persistence fails.
 */
export function saveTodos(todos: Todo[]): void {
  if (!storageAvailable()) {
    throw new Error('Local storage is not available. Changes cannot be saved.');
  }
  try {
    const serialized = JSON.stringify(todos);
    localStorage.setItem(STORAGE_KEY, serialized);
  } catch (err) {
    throw new Error('Failed to save todos. Your changes may not persist.');
  }
}

# File: src/hooks/useTodos.ts
import { useCallback, useMemo, useReducer, useState } from 'react';
import type { Todo } from '../types/todo';
import { generateId } from '../utils/id';
import { loadTodos, saveTodos } from '../utils/storage';

/**
 * Maximum allowed length for a todo title.
 * Long titles reduce readability and may degrade UX.
 */
export const MAX_TITLE_LENGTH = 120;

/**
 * Validate a todo title. Exported for testing.
 */
export function validateTodoTitle(rawTitle: string): { valid: boolean; message?: string; normalized?: string } {
  if (typeof rawTitle !== 'string') {
    return { valid: false, message: 'Title must be a string.' };
  }
  const trimmed = rawTitle.trim().replace(/\s+/g, ' '); // normalize whitespace
  if (trimmed.length === 0) {
    return { valid: false, message: 'Please enter a todo title.' };
  }
  if (trimmed.length > MAX_TITLE_LENGTH) {
    return { valid: false, message: `Title is too long (max ${MAX_TITLE_LENGTH} characters).` };
  }
  // Optional: basic control character protection
  if (/[\u0000-\u001F\u007F]/.test(trimmed)) {
    return { valid: false, message: 'Title contains invalid characters.' };
  }
  return { valid: true, normalized: trimmed };
}

/**
 * Actions supported by the todo reducer.
 */
type TodoAction =
  | { type: 'add'; title: string }
  | { type: 'toggle'; id: string }
  | { type: 'delete'; id: string }
  | { type: 'hydrate'; todos: Todo[] };

/**
 * Pure reducer function for todos. Exported for unit testing.
 */
export function todoReducer(state: Todo[], action: TodoAction): Todo[] {
  switch (action.type) {
    case 'hydrate': {
      return Array.isArray(action.todos) ? action.todos.slice() : state;
    }
    case 'add': {
      const id = generateId();
      const now = Date.now();
      const newTodo: Todo = {
        id,
        title: action.title,
        completed: false,
        createdAt: now
      };
      return [newTodo, ...state];
    }
    case 'toggle': {
      let changed = false;
      const next = state.map((t) => {
        if (t.id === action.id) {
          changed = true;
          return { ...t, completed: !t.completed };
        }
        return t;
      });
      return changed ? next : state;
    }
    case 'delete': {
      const next = state.filter((t) => t.id !== action.id);
      return next.length === state.length ? state : next;
    }
    default: {
      // Exhaustive check
      const _exhaustive: never = action;
      return state;
    }
  }
}

/**
 * Custom hook managing the todo list state with persistence and error handling.
 */
export function useTodos(): {
  todos: Todo[];
  addTodo: (title: string) => { success: boolean; error?: string };
  toggleTodo: (id: string) => void;
  deleteTodo: (id: string) => void;
  error: string | null;
  clearError: () => void;
} {
  // Initialize from storage exactly once using reducer initializer.
  const initializer = useCallback(() => {
    const { todos, error } = loadTodos();
    return { initialTodos: todos, initialError: error };
  }, []);

  const init = initializer();
  const [todos, dispatch] = useReducer(todoReducer, init.initialTodos);
  const [error, setError] = useState<string | null>(init.initialError);

  // Persist changes on each todos mutation.
  const persist = useCallback((next: Todo[]) => {
    try {
      saveTodos(next);
      // If previously had error from storage, clear it on successful save.
      if (error) setError(null);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unexpected error while saving.';
      setError(msg);
      // Do not rethrow; we allow in-memory state to continue working.
    }
  }, [error]);

  // Wrap dispatch to persist on state updates.
  const addTodo = useCallback((title: string) => {
    const v = validateTodoTitle(title);
    if (!v.valid) {
      return { success: false, error: v.message };
    }
    // Compose new state without mutating to persist atomically.
    const next = todoReducer(todos, { type: 'add', title: v.normalized! });
    dispatch({ type: 'add', title: v.normalized! });
    persist(next);
    return { success: true };
  }, [todos, persist]);

  const toggleTodo = useCallback((id: string) => {
    if (!id) return;
    const next = todoReducer(todos, { type: 'toggle', id });
    if (next === todos) {
      // No-op if id not found; surface a non-blocking error
      setError('Item not found. It may have been removed.');
      return;
    }
    dispatch({ type: 'toggle', id });
    persist(next);
  }, [todos, persist]);

  const deleteTodo = useCallback((id: string) => {
    if (!id) return;
    const next = todoReducer(todos, { type: 'delete', id });
    if (next === todos) {
      setError('Item not found. It may have been removed.');
      return;
    }
    dispatch({ type: 'delete', id });
    persist(next);
  }, [todos, persist]);

  const clearError = useCallback(() => setError(null), []);

  // Memoize returned values for stable references in children.
  return useMemo(() => ({
    todos,
    addTodo,
    toggleTodo,
    deleteTodo,
    error,
    clearError
  }), [todos, addTodo, toggleTodo, deleteTodo, error, clearError]);
}

# File: src/components/TodoInput.tsx
import React, { useCallback, useEffect, useId, useMemo, useState } from 'react';
import { MAX_TITLE_LENGTH, validateTodoTitle } from '../hooks/useTodos';

interface TodoInputProps {
  /**
   * Adds a new todo. Returns a result with success flag and optional error message.
   */
  onAdd: (title: string) => { success: boolean; error?: string };
}

/**
 * Controlled input component for adding todos with inline validation.
 */
export const TodoInput: React.FC<TodoInputProps> = ({ onAdd }) => {
  const inputId = useId();
  const [value, setValue] = useState('');
  const [touched, setTouched] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const validation = useMemo(() => validateTodoTitle(value), [value]);

  useEffect(() => {
    // Clear prior submit errors when user edits
    if (submitError) setSubmitError(null);
  }, [value, submitError]);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
  }, []);

  const handleBlur = useCallback(() => setTouched(true), []);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    // Prevent submission if invalid
    if (!validation.valid) {
      return;
    }
    const result = onAdd(validation.normalized!);
    if (result.success) {
      setValue('');
      setSubmitError(null);
    } else {
      setSubmitError(result.error ?? 'Failed to add item.');
    }
  }, [onAdd, validation]);

  const showError = (touched && !validation.valid) || !!submitError;
  const errorMessage = submitError || validation.message;

  return (
    <form onSubmit={handleSubmit} noValidate className="todo-input-form">
      <div className="field">
        <label htmlFor={inputId} className="label">New todo</label>
        <div className="input-row">
          <input
            id={inputId}
            name="title"
            type="text"
            className={`input ${showError ? 'input-error' : ''}`}
            placeholder="e.g., Buy groceries"
            value={value}
            onChange={handleChange}
            onBlur={handleBlur}
            aria-invalid={showError}
            aria-describedby={showError ? `${inputId}-error` : undefined}
            maxLength={MAX_TITLE_LENGTH}
            autoComplete="off"
            autoCapitalize="sentences"
          />
          <button
            type="submit"
            className="btn"
            disabled={!validation.valid}
            aria-disabled={!validation.valid}
            title="Add todo"
          >
            Add
          </button>
        </div>
        {showError && (
          <p id={`${inputId}-error`} role="alert" className="error-text">
            {errorMessage}
          </p>
        )}
      </div>
    </form>
  );
};

# File: src/components/TodoList.tsx
import React from 'react';
import type { Todo } from '../types/todo';
import { TodoItem } from './TodoItem';

interface TodoListProps {
  todos: Todo[];
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

/**
 * Renders a list of todo items or an empty state.
 */
export const TodoList: React.FC<TodoListProps> = ({ todos, onToggle, onDelete }) => {
  if (!todos || todos.length === 0) {
    return (
      <div className="empty-state" role="status" aria-live="polite">
        Your list is empty. Add a todo to get started!
      </div>
    );
  }

  return (
    <ul className="todo-list" role="list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={() => onToggle(todo.id)}
          onDelete={() => onDelete(todo.id)}
        />
      ))}
    </ul>
  );
};

# File: src/components/TodoItem.tsx
import React, { useCallback } from 'react';
import type { Todo } from '../types/todo';

interface TodoItemProps {
  todo: Todo;
  onToggle: () => void;
  onDelete: () => void;
}

/**
 * Todo item row with checkbox and delete actions.
 * Uses semantic elements for accessibility.
 */
export const TodoItem: React.FC<TodoItemProps> = ({ todo, onToggle, onDelete }) => {
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLButtonElement>) => {
    // Allow Enter/Space to activate delete button
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onDelete();
    }
  }, [onDelete]);

  return (
    <li className="todo-item">
      <label className="checkbox-label">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={onToggle}
          aria-label={`Mark