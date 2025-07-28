from PPlay.window import *
from PPlay.mouse import *
from constants import *
from asset_manager import AssetManager
from scenes import Menu, Dificuldade, Ranking, Jogar, GameOverScreen

def main():
    janela = Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    janela.set_title(GAME_TITLE)

    assets = AssetManager()
    assets.set_volume(GAME_VOLUME)

    mouse = Mouse()
    mouse_was_pressed = False
    
    # Dicionário central para o estado do jogo
    game_state = {
        "current_scene": GAME_STATE_MENU,
        "difficulty": DIFFICULTY_MEDIUM
    }
    
    # Instâncias das cenas
    menu_screen = Menu(janela)
    difficulty_screen = Dificuldade(janela)
    
    game_instance = None
    game_over_instance = None
    final_score = 0

    while game_state["current_scene"] != GAME_STATE_EXIT:
        janela.set_background_color(BACKGROUND_COLOR)
        
        mouse_is_pressed = mouse.is_button_pressed(1)
        is_new_click = mouse_is_pressed and not mouse_was_pressed
        mouse_was_pressed = mouse_is_pressed
        
        if not assets.background_music.is_playing():
            assets.background_music.play()

        current_scene_key = game_state["current_scene"]

        if current_scene_key == GAME_STATE_MENU:
            game_state["current_scene"] = menu_screen.run(is_new_click)
        
        elif current_scene_key == GAME_STATE_DIFFICULTY:
            # --- CORREÇÃO APLICADA AQUI ---
            # Passa o dicionário game_state para a função run
            game_state["current_scene"] = difficulty_screen.run(is_new_click, game_state)

        elif current_scene_key == GAME_STATE_PLAYING:
            if not game_instance:
                selected_settings = DIFFICULTY_SETTINGS[game_state["difficulty"]]
                game_instance = Jogar(janela, assets, selected_settings)
            
            next_scene, score = game_instance.run()
            if next_scene != GAME_STATE_PLAYING:
                final_score = score
                game_state["current_scene"] = next_scene
                game_instance = None
        
        elif current_scene_key == GAME_STATE_RANKING:
            ranking_screen = Ranking(janela)
            game_state["current_scene"] = ranking_screen.run(is_new_click)
        
        elif current_scene_key == GAME_STATE_GAME_OVER:
            if not game_over_instance:
                # Passa a dificuldade atual para a tela de game over
                game_over_instance = GameOverScreen(janela, final_score, game_state["difficulty"])
            
            next_scene = game_over_instance.run()
            if next_scene != GAME_STATE_GAME_OVER:
                game_state["current_scene"] = next_scene
                game_over_instance = None

        janela.update()

if __name__ == "__main__":
    main()