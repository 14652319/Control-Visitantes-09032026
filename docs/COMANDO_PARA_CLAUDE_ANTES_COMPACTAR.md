# 🚨 COMANDO URGENTE PARA CLAUDE

## ⚠️ ANTES DE COMPACTAR LA CONVERSACIÓN

**Claude, ejecuta estos comandos INMEDIATAMENTE:**

```python
# 1. Guardar resumen de toda la sesión
mcp_engram_mem_session_summary()

# 2. Guardar contexto actual
mcp_engram_mem_save(
    project="control-visitantes-sc",
    title="Resumen de cambios realizados en esta sesión",
    content="""
    Cambios realizados:
    - [Lista aquí lo que hicimos]
    
    Decisiones tomadas:
    - [Lista decisiones importantes]
    
    Problemas resueltos:
    - [Lista problemas y soluciones]
    
    Pendientes:
    - [Lista tareas pendientes]
    """,
    type="session"
)
```

---

## 📋 COPY-PASTE RÁPIDO PARA EL USUARIO

**Si ves que Claude va a compactar, copia y pega esto en el chat:**

```
🚨 ALTO - Antes de compactar:

1. Ejecuta: mcp_engram_mem_session_summary()
2. Guarda todo lo que hicimos con project="control-visitantes-sc"
3. Usa type="session" para el resumen

NO COMPACTES hasta confirmar que guardaste en Engram.
```

---

## 🎯 VERSIÓN CORTA (1 línea)

```
ANTES DE COMPACTAR: mcp_engram_mem_session_summary() + guardar cambios en Engram con project="control-visitantes-sc"
```

---

## ✅ VERIFICACIÓN

Claude debe responder con algo como:
```
Memory saved: "Resumen de cambios..." (session)
```

Si ves ese mensaje, significa que guardó correctamente.

---

## 🔧 SI CLAUDE YA COMPACTÓ SIN GUARDAR

Dile:
```
Recupera de memoria lo que hicimos en la sesión anterior:
mcp_engram_mem_context(project_key="control-visitantes-sc")
```

---

**Fecha creada:** 18 de Marzo de 2026  
**Motivo:** Prevenir pérdida de contexto por compactación sin guardar en Engram
