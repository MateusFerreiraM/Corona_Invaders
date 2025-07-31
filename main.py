from PPlay.window import *
from PPlay.mouse import *
from constants import *
from asset_manager import AssetManager
from scenes import ComoJogar, Menu, Dificuldade, Ranking, Jogar, GameOverScreen

def main():
    """Função principal que inicializa e executa o loop do jogo."""
    # --- Inicialização ---
    janela = Window(WINDOW_WIDTH, WINDOW_HEIGHT)
    janela.set_title(GAME_TITLE)

    assets = AssetManager()
    assets.set_volume(GAME_VOLUME)

    mouse = Mouse()
    mouse_was_pressed = False
    
    # --- Dicionário de Estado do Jogo ---
    game_state = {
        "current_scene": GAME_STATE_MENU,
        "difficulty": DIFFICULTY_MEDIUM
    }
    
    # --- Instâncias das Cenas (inicializadas como None) ---
    menu_screen = Menu(janela)
    difficulty_screen = None
    how_to_play_screen = None
    ranking_screen = None
    game_instance = None
    game_over_instance = None
    final_score = 0

    # =========================================================================================
    # --- Loop Principal do Jogo ---
    # =========================================================================================
    while game_state["current_scene"] != GAME_STATE_EXIT:
        janela.set_background_color(BACKGROUND_COLOR)
        
        # Controle de clique único do mouse
        mouse_is_pressed = mouse.is_button_pressed(1)
        is_new_click = mouse_is_pressed and not mouse_was_pressed
        mouse_was_pressed = mouse_is_pressed
        
        # Garante que a música de fundo continue tocando
        if not assets.background_music.is_playing():
            assets.background_music.play()

        current_scene_key = game_state["current_scene"]

        # =========================================================================================
        # --- Gerenciador de Cenas (State Machine) ---
        # =========================================================================================
        if current_scene_key == GAME_STATE_MENU:
            game_state["current_scene"] = menu_screen.run(is_new_click)
            
        elif current_scene_key == GAME_STATE_DIFFICULTY:
            if not difficulty_screen: difficulty_screen = Dificuldade(janela)
            game_state["current_scene"] = difficulty_screen.run(is_new_click, game_state)
            if game_state["current_scene"] == GAME_STATE_MENU: difficulty_screen = None # Reseta ao sair

        elif current_scene_key == GAME_STATE_HOW_TO_PLAY:
            if not how_to_play_screen: how_to_play_screen = ComoJogar(janela)
            game_state["current_scene"] = how_to_play_screen.run(is_new_click)
            if game_state["current_scene"] == GAME_STATE_MENU: how_to_play_screen = None

        elif current_scene_key == GAME_STATE_PLAYING:
            if not game_instance:
                selected_settings = DIFFICULTY_SETTINGS[game_state["difficulty"]]
                game_instance = Jogar(janela, assets, selected_settings)
            
            next_scene, score = game_instance.run(is_new_click)
            if next_scene != GAME_STATE_PLAYING:
                final_score = score
                game_state["current_scene"] = next_scene
                game_instance = None
        
        elif current_scene_key == GAME_STATE_RESTART:
            game_instance = None
            game_state["current_scene"] = GAME_STATE_PLAYING

        elif current_scene_key == GAME_STATE_RANKING:
            if not ranking_screen: ranking_screen = Ranking(janela)
            game_state["current_scene"] = ranking_screen.run(is_new_click)
            if game_state["current_scene"] == GAME_STATE_MENU: ranking_screen = None
        
        elif current_scene_key == GAME_STATE_GAME_OVER:
            if not game_over_instance:
                game_over_instance = GameOverScreen(janela, final_score, game_state["difficulty"])
            
            next_scene = game_over_instance.run()
            if next_scene != GAME_STATE_GAME_OVER:
                game_state["current_scene"] = next_scene
                game_over_instance = None

        janela.update()

if __name__ == "__main__":
    main()