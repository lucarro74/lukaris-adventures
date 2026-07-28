import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

ANCHO, ALTO = 800, 600
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Lukaris Adventures - Edición Pong de Reinos")

BG_PASTEL = (245, 230, 240)
TEXTO_OSCURO = (50, 40, 60)
ROSA_PASTEL = (255, 182, 193)
CELESTE_PASTEL = (173, 216, 230)
VERDE_PASTEL = (152, 251, 152)
LILA_PASTEL = (221, 160, 221)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
TECLADO_BG = (70, 60, 80)
TECLA_COLOR = (230, 215, 240)
TECLA_HOVER = (250, 235, 255)

fuente_titulo = pygame.font.SysFont(None, 55)
fuente_grande = pygame.font.SysFont(None, 36)
fuente_mediana = pygame.font.SysFont(None, 24)
fuente_chica = pygame.font.SysFont(None, 18)

def generar_sonido(frecuencia, duracion, tipo="beep"):
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * (duracion / 1000.0))
        buffer = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            if tipo == "beep":
                val = int(32767 * 0.5 * (1.0 if (int(t * frecuencia * 2) % 2 == 0) else -1.0))
            elif tipo == "explosion":
                val = int(32767 * 0.5 * (random.random() * 2 - 1))
            else:
                val = int(32767 * 0.5 * pygame.math.sin(2 * 3.1416 * frecuencia * t))
            buffer.extend(val.to_bytes(2, byteorder='little', signed=True))
        return pygame.mixer.Sound(buffer=bytes(buffer))
    except Exception:
        return None

sonido_clic = generar_sonido(600, 80)
sonido_rebote = generar_sonido(400, 50)
sonido_gol = generar_sonido(200, 200, "explosion")

FRASES = [
    "¡Un verdadero héroe nunca se rinde ante la adversidad, {nombre}!",
    "Cada obstáculo superado te acerca más a la gloria eterna, {nombre}.",
    "El poder de los reinos descansa sobre tus hombros, {nombre}.",
    "Forja tu propio destino con valor y sabiduría, {nombre}."
]

jugador = {
    "nombre": "",
    "titulo": "Rey",
    "color_ropa": (0, 100, 255),
    "forma": "Rectángulo",
    "arma": "Espada de Luz",
    "dificultad": "Normal",
    "puntuacion": 0,
    "tipo_sonido": "Aventurera"
}

REINOS = [
    {"id": 1, "nombre": "Reino de Aethel", "juego": "Pong Clásico", "color": (30, 30, 50), "animal": "Lobo de Cristal"},
    {"id": 2, "nombre": "Valle de Pyra", "juego": "Obstáculo Central Bloqueador", "color": (80, 20, 20), "animal": "Fénix de Fuego"},
    {"id": 3, "nombre": "Bosque Susurrante", "juego": "Poder: Muro Protector Temporal", "color": (20, 60, 30), "animal": "Ciervo Místico"},
    {"id": 4, "nombre": "Abismo de Caelum", "juego": "Pelota Microscópica Veloz", "color": (20, 30, 80), "animal": "Águila Celestial"},
    {"id": 5, "nombre": "Tierras Oscuras", "juego": "¡Inverso! Perder rebotes resta puntos", "color": (40, 20, 20), "animal": "Dragón Sombrío"},
    {"id": 6, "nombre": "Rey de Reyes / Reina de Reinas", "juego": "Desafío Definitivo Supremo", "color": (100, 80, 20), "animal": "Fénix Ancestral"}
]

reino_actual_idx = 0
objetivos_completados = 0
estado_juego = "MENU"
frase_actual = ""
input_texto = ""

TECLADO_FILAS = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ñ"],
    ["Z", "X", "C", "V", "B", "N", "M", "⌫"]
]

pelota_x = ANCHO // 2
pelota_y = ALTO // 2
pelota_vel_x = 4
pelota_vel_y = 3
paleta_jugador_y = ALTO // 2 - 40
paleta_ia_y = ALTO // 2 - 40
puntos_jugador = 0
puntos_ia = 0

# Variables para poderes especiales del Reino 3
poder_activo = False
tiempo_poder = 0

reloj = pygame.time.Clock()

def obtener_frase_personalizada():
    nombre_val = jugador["nombre"] if jugador["nombre"] != "" else "Guerrero"
    f = random.choice(FRASES)
    return f.format(nombre=nombre_val)

def dibujar_boton(texto, x, y, w, h, color_base, color_texto=NEGRO):
    mouse_pos = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    rect = pygame.Rect(x, y, w, h)
    activo = rect.collidepoint(mouse_pos)
    
    color_actual = (min(color_base[0]+30, 255), min(color_base[1]+30, 255), min(color_base[2]+30, 255)) if activo else color_base
    
    pygame.draw.rect(pantalla, color_actual, rect, border_radius=10)
    pygame.draw.rect(pantalla, NEGRO, rect, 2, border_radius=10)
    
    txt_surf = fuente_mediana.render(texto, True, color_texto)
    pantalla.blit(txt_surf, (x + (w - txt_surf.get_width()) // 2, y + (h - txt_surf.get_height()) // 2))
    
    return activo and click[0]

def reiniciar_pelota():
    global pelota_x, pelota_y, pelota_vel_x, pelota_vel_y
    pelota_x = ANCHO // 2
    pelota_y = ALTO // 2
    pelota_vel_x = -4 if random.random() > 0.5 else 4
    pelota_vel_y = -3 if random.random() > 0.5 else 3

def dibujar_forma_jugador(x, y, forma, color):
    if forma == "Rectángulo":
        pygame.draw.rect(pantalla, color, (x, y, 15, 80), border_radius=4)
    elif forma == "Escudo":
        pygame.draw.rect(pantalla, color, (x - 2, y, 19, 80), border_radius=8)
    elif forma == "Cuchilla":
        pygame.draw.polygon(pantalla, color, [(x + 15, y), (x, y + 40), (x + 15, y + 80)])
    elif forma == "Orbe Mágico":
        pygame.draw.circle(pantalla, color, (x + 7, y + 40), 25)

moviendo_arriba = False
moviendo_abajo = False

while True:
    pantalla.fill(BG_PASTEL)
    
    eventos = pygame.event.get()
    mouse_pos_actual = pygame.mouse.get_pos()
    
    for evento in eventos:
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
                        
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = evento.pos
            if sonido_clic: sonido_clic.play()
            
            if estado_juego == "MENU":
                if 250 <= mouse_x <= 550:
                    if 180 <= mouse_y <= 230:
                        frase_actual = obtener_frase_personalizada()
                        estado_juego = "REGISTRO"
                    elif 240 <= mouse_y <= 290:
                        estado_juego = "SELECCION_REINO"
                    elif 300 <= mouse_y <= 350:
                        estado_juego = "INSTRUCCIONES"
                    elif 360 <= mouse_y <= 410:
                        estado_juego = "CONFIG_SONIDO"
                    elif 420 <= mouse_y <= 470:
                        print("Partida guardada correctamente.")
                    elif 480 <= mouse_y <= 530:
                        pygame.quit()
                        sys.exit()
                        
            elif estado_juego == "REGISTRO":
                teclado_y_inicio = 120
                for fila_idx, fila in enumerate(TECLADO_FILAS):
                    teclas_en_fila = len(fila)
                    ancho_tecla = 45
                    alto_tecla = 40
                    espacio = 6
                    ancho_total = teclas_en_fila * ancho_tecla + (teclas_en_fila - 1) * espacio
                    inicio_x = (ANCHO - ancho_total) // 2
                    
                    for col_idx, tecla in enumerate(fila):
                        tx = inicio_x + col_idx * (ancho_tecla + espacio)
                        ty = teclado_y_inicio + fila_idx * (alto_tecla + espacio)
                        
                        if pygame.Rect(tx, ty, ancho_tecla, alto_tecla).collidepoint(mouse_x, mouse_y):
                            if tecla == "⌫":
                                input_texto = input_texto[:-1]
                            else:
                                if len(input_texto) < 12:
                                    input_texto += tecla

                if 310 <= mouse_x <= 370 and 315 <= mouse_y <= 345:
                    jugador["titulo"] = "Rey"
                elif 380 <= mouse_x <= 450 and 315 <= mouse_y <= 345:
                    jugador["titulo"] = "Reina"
                elif 100 <= mouse_x <= 165 and 385 <= mouse_y <= 415:
                    jugador["color_ropa"] = (0, 100, 255)
                elif 175 <= mouse_x <= 240 and 385 <= mouse_y <= 415:
                    jugador["color_ropa"] = (255, 105, 180)
                elif 250 <= mouse_x <= 315 and 385 <= mouse_y <= 415:
                    jugador["color_ropa"] = (50, 205, 50)
                elif 325 <= mouse_x <= 390 and 385 <= mouse_y <= 415:
                    jugador["color_ropa"] = (255, 215, 0)
                elif 420 <= mouse_x <= 535 and 380 <= mouse_y <= 410:
                    jugador["forma"] = "Rectángulo"
                elif 545 <= mouse_x <= 645 and 380 <= mouse_y <= 410:
                    jugador["forma"] = "Escudo"
                elif 420 <= mouse_x <= 535 and 420 <= mouse_y <= 450:
                    jugador["forma"] = "Cuchilla"
                elif 545 <= mouse_x <= 645 and 420 <= mouse_y <= 450:
                    jugador["forma"] = "Orbe Mágico"
                elif 300 <= mouse_x <= 500 and 520 <= mouse_y <= 565:
                    if input_texto.strip() != "":
                        jugador["nombre"] = input_texto.strip()
                    else:
                        jugador["nombre"] = "Guerrero"
                    estado_juego = "DIFICULTAD"
                    
            elif estado_juego == "DIFICULTAD":
                if 250 <= mouse_x <= 550:
                    if 180 <= mouse_y <= 230:
                        jugador["dificultad"] = "Fácil"
                        estado_juego = "JUGANDO"
                    elif 250 <= mouse_y <= 300:
                        jugador["dificultad"] = "Normal"
                        estado_juego = "JUGANDO"
                    elif 320 <= mouse_y <= 370:
                        jugador["dificultad"] = "Difícil"
                        estado_juego = "JUGANDO"
                    elif 390 <= mouse_y <= 440:
                        jugador["dificultad"] = "Súper Difícil"
                        estado_juego = "JUGANDO"

            elif estado_juego == "SELECCION_REINO":
                if 50 <= mouse_x <= 200 and 530 <= mouse_y <= 570:
                    estado_juego = "MENU"
                else:
                    y_pos = 65
                    for r in REINOS:
                        if 150 <= mouse_x <= 650 and y_pos <= mouse_y <= y_pos + 35:
                            reino_actual_idx = r['id'] - 1
                            objetivos_completados = 0
                            puntos_jugador = 0
                            puntos_ia = 0
                            reiniciar_pelota()
                            estado_juego = "JUGANDO"
                            break
                        y_pos += 40

            elif estado_juego == "INSTRUCCIONES":
                if 300 <= mouse_x <= 500 and 500 <= mouse_y <= 550:
                    estado_juego = "MENU"

            elif estado_juego == "CONFIG_SONIDO":
                if 200 <= mouse_x <= 400 and 220 <= mouse_y <= 270:
                    jugador["tipo_sonido"] = "Aventurera"
                elif 450 <= mouse_x <= 650 and 220 <= mouse_y <= 270:
                    jugador["tipo_sonido"] = "Épica Sinfónica"
                elif 200 <= mouse_x <= 400 and 300 <= mouse_y <= 350:
                    jugador["tipo_sonido"] = "Electrónica Chiptune"
                elif 450 <= mouse_x <= 650 and 300 <= mouse_y <= 350:
                    jugador["tipo_sonido"] = "Ambiental Calma"
                elif 300 <= mouse_x <= 500 and 420 <= mouse_y <= 470:
                    estado_juego = "MENU"

            elif estado_juego == "JUGANDO":
                if 20 <= mouse_x <= 100 and 20 <= mouse_y <= 60:
                    estado_juego = "PAUSA"
                elif 120 <= mouse_x <= 250 and 20 <= mouse_y <= 60:
                    objetivos_completados += 1
                    if objetivos_completados >= 10:
                        reino_actual_idx += 1
                        objetivos_completados = 0
                        puntos_jugador = 0
                        puntos_ia = 0
                        reiniciar_pelota()
                        if reino_actual_idx >= len(REINOS):
                            estado_juego = "CORONACION"

            elif estado_juego == "PAUSA":
                if 300 <= mouse_x <= 500 and 220 <= mouse_y <= 280:
                    estado_juego = "JUGANDO"
                elif 300 <= mouse_x <= 500 and 300 <= mouse_y <= 360:
                    estado_juego = "MENU"

            elif estado_juego == "CORONACION":
                if 250 <= mouse_x <= 550 and 450 <= mouse_y <= 510:
                    reino_actual_idx = 0
                    objetivos_completados = 0
                    estado_juego = "MENU"

        elif evento.type == pygame.KEYDOWN:
            if estado_juego == "REGISTRO":
                if evento.key == pygame.K_BACKSPACE:
                    input_texto = input_texto[:-1]
                elif evento.key == pygame.K_RETURN:
                    if input_texto.strip() != "":
                        jugador["nombre"] = input_texto.strip()
                    else:
                        jugador["nombre"] = "Guerrero"
                    estado_juego = "DIFICULTAD"
                else:
                    if len(input_texto) < 12 and evento.unicode.isalnum():
                        input_texto += evento.unicode.upper()
            elif estado_juego == "JUGANDO" and reino_actual_idx == 2:
                # Reino 3: Presionar ESPACIO activa el muro protector temporal
                if evento.key == pygame.K_SPACE and not poder_activo:
                    poder_activo = True
                    tiempo_poder = pygame.time.get_ticks()

        elif evento.type == pygame.MOUSEBUTTONUP:
            if estado_juego == "JUGANDO":
                moviendo_arriba = False
                moviendo_abajo = False

    keys = pygame.key.get_pressed()
    if estado_juego == "JUGANDO":
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        
        btn_subir_rect = pygame.Rect(ANCHO - 160, ALTO - 140, 65, 55)
        btn_bajar_rect = pygame.Rect(ANCHO - 160, ALTO - 75, 65, 55)
        
        if mouse_pressed[0]:
            if btn_subir_rect.collidepoint(mouse_pos):
                moviendo_arriba = True
            elif btn_bajar_rect.collidepoint(mouse_pos):
                moviendo_abajo = True
            else:
                moviendo_arriba = False
                moviendo_abajo = False
        else:
            moviendo_arriba = False
            moviendo_abajo = False

        # Ajuste de velocidad según dificultad
        velocidad_paleta = 6
        if jugador["dificultad"] == "Fácil": velocidad_paleta = 5
        elif jugador["dificultad"] == "Difícil": velocidad_paleta = 7
        elif jugador["dificultad"] == "Súper Difícil": velocidad_paleta = 8

        if keys[pygame.K_UP] or keys[pygame.K_w] or moviendo_arriba:
            paleta_jugador_y -= velocidad_paleta
        if keys[pygame.K_DOWN] or keys[pygame.K_s] or moviendo_abajo:
            paleta_jugador_y += velocidad_paleta
            
        if paleta_jugador_y < 70:
            paleta_jugador_y = 70
        if paleta_jugador_y > ALTO - 110:
            paleta_jugador_y = ALTO - 110

        # Ajuste de velocidad de pelota por Reino y Dificultad
        vel_multiplicador = 1.0
        if reino_actual_idx == 3: # Reino 4: Pelota ultra veloz
            vel_multiplicador = 1.8
        elif reino_actual_idx == 5: # Reino 6: Ultra caótico y difícil
            vel_multiplicador = 2.2
            
        if jugador["dificultad"] == "Súper Difícil":
            vel_multiplicador *= 1.3

        pelota_x += int(pelota_vel_x * vel_multiplicador)
        pelota_y += int(pelota_vel_y * vel_multiplicador)

        if pelota_y <= 70 or pelota_y >= ALTO - 20:
            pelota_vel_y *= -1
            if sonido_rebote: sonido_rebote.play()

        # IA con dificultad dinámica
        velocidade_ia = 3.5
        if jugador["dificultad"] == "Difícil": velocidade_ia = 5.0
        elif jugador["dificultad"] == "Súper Difícil": velocidade_ia = 6.5
        
        if paleta_ia_y + 40 < pelota_y:
            paleta_ia_y += velocidade_ia
        elif paleta_ia_y + 40 > pelota_y:
            paleta_ia_y -= velocidade_ia

        if paleta_ia_y < 70: paleta_ia_y = 70
        if paleta_ia_y > ALTO - 110: paleta_ia_y = ALTO - 110

        # Tamaños de pelota según reino
        tam_pelota = 15
        if reino_actual_idx == 3: # Reino 4: Pelota pequeña y difícil
            tam_pelota = 8

        if jugador["forma"] == "Orbe Mágico":
            rect_jugador = pygame.Rect(50, paleta_jugador_y + 15, 25, 50)
        else:
            rect_jugador = pygame.Rect(50, paleta_jugador_y, 15, 80)
            
        rect_ia = pygame.Rect(ANCHO - 65, paleta_ia_y, 15, 80)
        rect_pelota = pygame.Rect(pelota_x, pelota_y, tam_pelota, tam_pelota)

        # Mecánica Reino 3: Desactivar poder a los 3 segundos
        if poder_activo and pygame.time.get_ticks() - tiempo_poder > 3000:
            poder_activo = False

        # Colisión con muro protector del Reino 3
        if reino_actual_idx == 2 and poder_activo:
            rect_muro = pygame.Rect(30, 70, 10, ALTO - 90)
            if rect_pelota.colliderect(rect_muro):
                pelota_vel_x *= -1
                if sonido_rebote: sonido_rebote.play()

        if rect_pelota.colliderect(rect_jugador):
            pelota_vel_x *= -1
            objetivos_completados += 1
            if sonido_rebote: sonido_rebote.play()

        if rect_pelota.colliderect(rect_ia):
            pelota_vel_x *= -1
            if sonido_rebote: sonido_rebote.play()

        # Mecánica Reino 5: Perder el rebote RESTA puntos en vez de sumar
        if pelota_x < 0:
            if reino_actual_idx == 4:
                objetivos_completados = max(0, objetivos_completados - 2)
            puntos_ia += 1
            if sonido_gol: sonido_gol.play()
            reiniciar_pelota()
        elif pelota_x > ANCHO:
            puntos_jugador += 1
            objetivos_completados += 2
            if sonido_gol: sonido_gol.play()
            reiniciar_pelota()

        if objetivos_completados >= 10:
            reino_actual_idx += 1
            objetivos_completados = 0
            puntos_jugador = 0
            puntos_ia = 0
            reiniciar_pelota()
            if reino_actual_idx >= len(REINOS):
                estado_juego = "CORONACION"

    if estado_juego == "MENU":
        titulo = fuente_titulo.render("Lukaris Adventures", True, TEXTO_OSCURO)
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 40))
        
        if dibujar_boton("Jugar", 250, 180, 300, 45, ROSA_PASTEL): pass
        if dibujar_boton("Seleccionar Reino", 250, 240, 300, 45, CELESTE_PASTEL): pass
        if dibujar_boton("Instrucciones", 250, 300, 300, 45, VERDE_PASTEL): pass
        if dibujar_boton("Sonido / Música", 250, 360, 300, 45, (255, 220, 150)): pass
        if dibujar_boton("Cargar / Reiniciar Partida", 250, 420, 300, 45, LILA_PASTEL): pass
        if dibujar_boton("Salir", 250, 480, 300, 45, (230, 150, 150)): pass

    elif estado_juego == "REGISTRO":
        tit = fuente_grande.render("Hola guerrero pon tu nombre", True, TEXTO_OSCURO)
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 10))
        
        rect_input = pygame.Rect(ANCHO // 2 - 125, 55, 250, 35)
        pygame.draw.rect(pantalla, BLANCO, rect_input, border_radius=5)
        pygame.draw.rect(pantalla, NEGRO, rect_input, 2, border_radius=5)
        
        txt_input_surf = fuente_mediana.render(input_texto, True, TEXTO_OSCURO)
        pantalla.blit(txt_input_surf, (rect_input.x + 15, rect_input.y + 6))
        
        teclado_y_inicio = 110
        for fila_idx, fila in enumerate(TECLADO_FILAS):
            teclas_en_fila = len(fila)
            ancho_tecla = 45
            alto_tecla = 40
            espacio = 6
            ancho_total = teclas_en_fila * ancho_tecla + (teclas_en_fila - 1) * espacio
            inicio_x = (ANCHO - ancho_total) // 2
            
            for col_idx, tecla in enumerate(fila):
                tx = inicio_x + col_idx * (ancho_tecla + espacio)
                ty = teclado_y_inicio + fila_idx * (alto_tecla + espacio)
                
                tecla_rect = pygame.Rect(tx, ty, ancho_tecla, alto_tecla)
                hover = tecla_rect.collidepoint(mouse_pos_actual)
                
                color_tecla = TECLA_HOVER if hover else TECLA_COLOR
                pygame.draw.rect(pantalla, color_tecla, tecla_rect, border_radius=6)
                pygame.draw.rect(pantalla, NEGRO, tecla_rect, 1, border_radius=6)
                
                t_surf = fuente_mediana.render(tecla, True, TEXTO_OSCURO)
                pantalla.blit(t_surf, (tx + (ancho_tecla - t_surf.get_width()) // 2, ty + (alto_tecla - t_surf.get_height()) // 2))
        
        lbl_tit = fuente_chica.render(f"Título: {jugador['titulo']}", True, TEXTO_OSCURO)
        pantalla.blit(lbl_tit, (310, 290))
        dibujar_boton("Rey", 310, 315, 60, 30, CELESTE_PASTEL)
        dibujar_boton("Reina", 380, 315, 70, 30, ROSA_PASTEL)
        
        lbl_col = fuente_chica.render("Color:", True, TEXTO_OSCURO)
        pantalla.blit(lbl_col, (100, 360))
        dibujar_boton("Azul", 100, 385, 65, 30, (0, 100, 255), BLANCO)
        dibujar_boton("Rosa", 175, 385, 65, 30, (255, 105, 180))
        dibujar_boton("Verde", 250, 385, 65, 30, (50, 205, 50))
        dibujar_boton("Oro", 325, 385, 65, 30, (255, 215, 0))
        
        lbl_form = fuente_chica.render(f"Forma: {jugador['forma']}", True, TEXTO_OSCURO)
        pantalla.blit(lbl_form, (420, 355))
        dibujar_boton("Rectángulo", 420, 380, 115, 30, VERDE_PASTEL)
        dibujar_boton("Escudo", 545, 380, 100, 30, CELESTE_PASTEL)
        dibujar_boton("Cuchilla", 420, 420, 115, 30, LILA_PASTEL)
        dibujar_boton("Orbe", 545, 420, 100, 30, ROSA_PASTEL)

        dibujar_boton("Continuar Partida", 300, 520, 200, 40, ROSA_PASTEL)

    elif estado_juego == "DIFICULTAD":
        tit = fuente_grande.render("Selecciona la Dificultad", True, TEXTO_OSCURO)
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 80))
        
        dibujar_boton("Fácil", 250, 180, 300, 45, VERDE_PASTEL)
        dibujar_boton("Normal", 250, 250, 300, 45, CELESTE_PASTEL)
        dibujar_boton("Difícil", 250, 320, 300, 45, ROSA_PASTEL)
        dibujar_boton("Súper Difícil", 250, 390, 300, 45, (255, 100, 100))

    elif estado_juego == "SELECCION_REINO":
        tit = fuente_grande.render("Selecciona un Reino (Variantes Únicas)", True, TEXTO_OSCURO)
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 20))
        
        y_pos = 65
        for r in REINOS:
            texto_reino = f"{r['id']}. {r['nombre']} - [{r['juego']}]"
            dibujar_boton(texto_reino, 100, y_pos, 600, 35, CELESTE_PASTEL)
            y_pos += 40
            
        dibujar_boton("Volver", 50, 530, 150, 35, (200, 200, 200))

    elif estado_juego == "INSTRUCCIONES":
        tit = fuente_grande.render("Instrucciones de los Reinos", True, TEXTO_OSCURO)
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 40))
        
        instrucciones_texto = [
            "- Reino 1: Pong Clásico tradicional.",
            "- Reino 2: Obstáculo central fijo que bloquea los rebotes.",
            "- Reino 3: Poder especial (Presiona ESPACIO para desplegar muro protector).",
            "- Reino 4: Pelota microscópica con velocidad extrema.",
            "- Reino 5: ¡Caos! Perder puntos o fallar penaliza tus objetivos.",
            "- Reino 6: ¡Rey/Reina de Reinos! Dificultad suprema y desafiante."
        ]
        
        y_ins = 100
        for linea in instrucciones_texto:
            txt = fuente_chica.render(linea, True, TEXTO_OSCURO)
            pantalla.blit(txt, (50, y_ins))
            y_ins += 35
            
        dibujar_boton("Volver", 300, 500, 200, 45, ROSA_PASTEL)

    elif estado_juego == "CONFIG_SONIDO":
        tit = fuente_grande.render("Configuración de Sonido y Música", True, TEXTO_OSCURO)
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 80))
        
        lbl_act = fuente_mediana.render(f"Sonido Actual: {jugador['tipo_sonido']}", True, TEXTO_OSCURO)
        pantalla.blit(lbl_act, (200, 150))
        
        dibujar_boton("Aventurera", 200, 220, 200, 40, CELESTE_PASTEL)
        dibujar_boton("Épica Sinfónica", 450, 220, 200, 40, VERDE_PASTEL)
        dibujar_boton("Electrónica", 200, 300, 200, 40, LILA_PASTEL)
        dibujar_boton("Ambiental Calma", 450, 300, 200, 40, ROSA_PASTEL)
        
        dibujar_boton("Guardar y Volver", 300, 420, 200, 45, (200, 200, 200))

    elif estado_juego == "JUGANDO":
        reino = REINOS[reino_actual_idx]
        pantalla.fill(reino['color'])
        
        dibujar_boton("Pausa", 20, 20, 80, 35, BLANCO)
        dibujar_boton("+1 Objetivo", 110, 20, 130, 35, BLANCO)
        
        txt_info = fuente_mediana.render(f"Reino {reino['id']}: {reino['nombre']} | {reino['juego']}", True, BLANCO)
        pantalla.blit(txt_info, (250, 25))
        
        txt_obj = fuente_mediana.render(f"Objetivos: {objetivos_completados} / 10", True, (255, 255, 0))
        pantalla.blit(txt_obj, (ANCHO - 180, 25))
        
        txt_frase = fuente_chica.render(frase_actual, True, BLANCO)
        pantalla.blit(txt_frase, (20, ALTO - 25))
        
        pygame.draw.aaline(pantalla, BLANCO, (ANCHO // 2, 70), (ANCHO // 2, ALTO - 30))
        
        # Elemento específico Reino 2: Obstáculo central bloqueador
        if reino_actual_idx == 1:
            obstaculo_rect = pygame.Rect(ANCHO // 2 - 10, ALTO // 2 - 50, 20, 100)
            pygame.draw.rect(pantalla, (255, 100, 100), obstaculo_rect, border_radius=5)
            if rect_pelota.colliderect(obstaculo_rect):
                pelota_vel_x *= -1
                if sonido_rebote: sonido_rebote.play()

        # Elemento específico Reino 3: Dibujar muro protector si el poder está activo
        if reino_actual_idx == 2 and poder_activo:
            pygame.draw.rect(pantalla, (0, 255, 255), (30, 70, 10, ALTO - 90), border_radius=3)
            txt_poder = fuente_chica.render("¡MURO PROTECTOR ACTIVO!", True, (0, 255, 255))
            pantalla.blit(txt_poder, (ANCHO // 2 - 100, 50))
        elif reino_actual_idx == 2:
            txt_poder_info = fuente_chica.render("Presiona [ESPACIO] para activar Muro Protector temporal", True, BLANCO)
            pantalla.blit(txt_poder_info, (ANCHO // 2 - 180, 50))

        dibujar_forma_jugador(50, paleta_jugador_y, jugador['forma'], jugador['color_ropa'])
        pygame.draw.rect(pantalla, (200, 50, 50), (ANCHO - 65, paleta_ia_y, 15, 80), border_radius=4)
        pygame.draw.ellipse(pantalla, BLANCO, (pelota_x, pelota_y, tam_pelota, tam_pelota))
        
        dibujar_boton("▲", ANCHO - 160, ALTO - 140, 65, 55, CELESTE_PASTEL)
        dibujar_boton("▼", ANCHO - 160, ALTO - 75, 65, 55, CELESTE_PASTEL)

    elif estado_juego == "PAUSA":
        pantalla.fill((30, 30, 40))
        tit = fuente_titulo.render("JUEGO EN PAUSA", True, BLANCO)
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 120))
        
        dibujar_boton("Reanudar", 300, 220, 200, 45, CELESTE_PASTEL)
        dibujar_boton("Menú Principal", 300, 300, 200, 45, ROSA_PASTEL)

    elif estado_juego == "CORONACION":
        pantalla.fill((50, 40, 20))
        tit = fuente_titulo.render("¡CEREMONIA DE CORONACIÓN SUPREMA!", True, (255, 215, 0))
        pantalla.blit(tit, (ANCHO // 2 - tit.get_width() // 2, 100))
        
        nombre_ganador = jugador["nombre"] if jugador["nombre"] != "" else "Guerrero"
        msj = fuente_grande.render(f"¡Eres el ganador, {jugador['titulo']} de los Reinos, {nombre_ganador}!", True, BLANCO)
        pantalla.blit(msj, (ANCHO // 2 - msj.get_width() // 2, 220))
        
        sub = fuente_mediana.render("Has superado todas las pruebas y reinos desafiantes de Lukaris Adventures.", True, (220, 220, 220))
        pantalla.blit(sub, (ANCHO // 2 - sub.get_width() // 2, 280))
        
        dibujar_boton("Volver al Inicio", 250, 450, 300, 50, VERDE_PASTEL)

    pygame.display.flip()
    reloj.tick(60)
