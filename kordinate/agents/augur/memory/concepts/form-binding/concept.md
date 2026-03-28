---
description: Form Binding — two-way or controlled data binding between form inputs and state
type: pattern
curated: true
scope: global
preloaded: none
graphable: false
abstraction: [frontend, data]
---
# Form Binding

## Recognition

How to identify this pattern in code.

### Signatures

- Controlled inputs with `value` + `onChange` handlers managing state (React)
- `react-hook-form` with `useForm`, `register`, `handleSubmit`, `Controller` (React)
- `formik` with `useFormik`, `<Formik>`, `<Field>`, `<Form>` (React)
- `v-model` directive for two-way binding on inputs, selects, textareas (Vue)
- `vee-validate` with `useForm`, `useField`, `<Form>`, `<Field>` (Vue)
- `ngModel` for template-driven forms, `FormControl`/`FormGroup`/`FormBuilder` for reactive forms (Angular)
- `bind:value` for two-way binding on form elements (Svelte)
- Zod, Yup, or Joi schemas used for form validation: `z.object()`, `yup.object().shape()`
- `zodResolver`, `yupResolver` connecting schema validation to form libraries
- Form submission handlers: `onSubmit`, `handleSubmit`, `@submit.prevent`
- Error display patterns: `errors.fieldName`, field-level error messages, touched state tracking
- Go: `echo.Bind()`, `c.Bind(&form)`, `gin.ShouldBind()` for server-side form binding to structs
- Go: `gorilla/schema` decoder for form data to struct mapping
- Go: template form rendering with `{{.Form.FieldName}}` and struct tag-based binding
- Java: Spring MVC `@ModelAttribute` and `BindingResult` for server-side form binding and validation

### Confidence

- **high** -- Form library (react-hook-form, Formik, vee-validate, Angular Reactive Forms) with schema validation, field registration, and structured error handling
- **medium** -- Framework two-way binding (v-model, ngModel, bind:value) with manual validation logic in submit handler
- **low** -- Uncontrolled form inputs read via refs or FormData at submit time, with no structured binding or validation

## Architecture

Look for a structured connection between form inputs and application state, with validation rules enforced before submission and error feedback displayed per field.

### Review Checklist

- Form state is managed by a form library or structured pattern, not scattered useState calls per field
- Validation schema is defined separately from UI and shared with backend if possible (Zod)
- Field-level errors are displayed adjacent to the relevant input, not just as a summary
- Form submission is disabled or guarded while validation errors exist
- Async validation (uniqueness checks, server-side rules) is handled without blocking the UI
- Form reset and dirty-state tracking are implemented for navigation guards and cancel actions

### Anti-patterns

- Individual `useState` for every form field instead of using a form library or reducer
- Validation only on submit, with no inline feedback as the user fills out fields
- Two-way binding on complex objects causing unexpected mutations (especially in Vue/Angular)
- No loading or disabled state on the submit button, allowing double submission
- Mixing controlled and uncontrolled inputs in the same form
