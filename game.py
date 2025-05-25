import pygame, asyncio, random, time
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Mark II Zombie Shooter")
        self.font = pygame.font.Font("./Fonts/Roboto-Regular.ttf", 12)
        self.endFont = pygame.font.Font("./Fonts/Roboto-Black.ttf", 36)
        self.clock = pygame.time.Clock()
        initialization_success = self.initialize_game()
        self.running = True
        self.dt = 0.0
        self.last_time = pygame.time.get_ticks()
        if not initialization_success:
            raise Exception("Game initialization failed")
    def initialize_game(self):
        self.character = type('Character', (), {})()
        self.character.pos = [375, 275]
        self.character.health = 100
        self.character.ammo = 10
        self.character.size = (50, 50)
        self.character.hitbox = pygame.Rect(self.character.pos[0], self.character.pos[1], *self.character.size)
        self.character.hitbox_color = (0, 0, 255)
        self.character.hitbox_active = True
        self.character.velocity_x = 0
        self.character.velocity_y = 0
        self.character.acceleration = 2000
        self.character.friction = 5

        self.kill_count = 0
        self.score = 0

        self.zombies = []
        self.zombie_count = 0
        self.zombie_spawn_rate = 1.0
        self.zombie_spawn_timer = 0.0
        self.zombie_spawn_limit = 10
        self.zombie_speed = 100
        self.zombie_damage = 10
        self.zombie_health = 50
        self.zombie_attack_range = 50
        self.zombie_attack_cooldown = 1.0
        self.zombie_attack_cooldown_timer = 0.0
        self.zombie_size = (50, 50)

        self.bullets = []
        self.bullet_speed = 500
        self.bullet_damage = 20
        self.bullet_spawn_rate = 0.5
        self.bullet_spawn_timer = 0.0
        self.bullet_spawn_limit = 100
        self.bullet_lifetime = 2.0
        self.bullet_size = (10, 5)
        self.bullet_cooldown = 0.2
        self.bullet_cooldown_timer = 0.0
        self.bullet_hitbox = pygame.Rect(0, 0, *self.bullet_size)
        self.bullet_hitbox.center = (self.character.pos[0] + 25, self.character.pos[1] + 25)
        self.bullet_hitbox_color = (255, 0, 0)
        self.bullet_hitbox_active = False
        print("Game initialized successfully.")
        return True
    def handle_input(self):
        for event in pygame.event.get():
            print(f"Event detected: {event}")
            if event.type == pygame.MOUSEBUTTONDOWN:
                print(f"Mouse button pressed at {pygame.mouse.get_pos()}.")

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            self.running = False
            print("Escape key pressed, exiting game.")
        if keys[pygame.K_w]:
            self.character.velocity_y = max(0, self.character.velocity_y + self.character.acceleration * self.dt)
        if keys[pygame.K_s]:
            self.character.velocity_y = min(0, self.character.velocity_y - self.character.acceleration * self.dt)
        if keys[pygame.K_a]:
            self.character.velocity_x = min(0, self.character.velocity_x - self.character.acceleration * self.dt)
        if keys[pygame.K_d]:
            self.character.velocity_x = max(0, self.character.velocity_x + self.character.acceleration * self.dt)
        if keys[pygame.K_SPACE]:
            self.shoot()
            print("Space key pressed, shooting action triggered.")
    def shoot(self):
        if self.character.ammo <= 0:
            print("No ammo left, cannot shoot.")
            return
        
        if self.bullet_cooldown_timer > 0:
            self.bullet_cooldown_timer -= self.dt
            if self.bullet_cooldown_timer < 0:
                self.bullet_cooldown_timer = 0
            return


        print("Shooting action executed.")
        self.bullet_hitbox_active = True
        self.bullet_hitbox.center = (self.character.pos[0] + 25, self.character.pos[1] + 25)
        self.bullet_cooldown_timer = self.bullet_cooldown
        self.bullets.append(self.bullet_hitbox.copy())
        self.character.ammo -= 1
        print(f"Bullet fired from position: {self.bullet_hitbox.center}")
        asyncio.run(self.reset_bullet_hitbox())
    async def reset_bullet_hitbox(self):
        self.bullet_hitbox_active = False
        self.bullet_hitbox = pygame.Rect(0, 0, *self.bullet_size)
        self.bullet_hitbox.center = (self.character.pos[0] + 25, self.character.pos[1] + 25)
    
    def zombie_hit(self, zombie):
        print(f"Zombie hit at position: {zombie.topleft}")
        self.zombies.remove(zombie)
        self.zombie_count -= 1
        print(f"Zombie removed, current count: {self.zombie_count}")

    def update_game_logic(self):

        self.character.pos[1] -= self.character.velocity_y * self.dt
        self.character.pos[0] += self.character.velocity_x * self.dt

        self.character.velocity_x *= (1 - self.character.friction * self.dt)
        self.character.velocity_y *= (1 - self.character.friction * self.dt)

        self.character.hitbox.topleft = (self.character.pos[0], self.character.pos[1])

        if self.zombie_count < self.zombie_spawn_limit:
            self.zombie_spawn_timer += self.dt
            if self.zombie_spawn_timer >= 1.0 / self.zombie_spawn_rate:
                self.zombie_spawn_timer = 0.0
                new_zombie = pygame.Rect(random.randint(600, 800), random.randint(0, 600), *self.zombie_size)
                self.zombies.append(new_zombie)
                self.zombie_count += 1
                print(f"New zombie spawned at {new_zombie.topleft}, total zombies: {self.zombie_count}")
        
        for zombie in self.zombies:
            zombie.x -= self.zombie_speed * self.dt
            if zombie.x < 0:
                self.zombies.remove(zombie)
                self.zombie_count -= 1
                self.character.health -= self.zombie_damage
                print(f"Zombie at {zombie.topleft} went off-screen, character health reduced to {self.character.health}.")
                if self.character.health <= 0:
                    self.running = False
                    print("Character health reached zero, game over.")

                print("Zombie removed from the game, it went off-screen.")

        for bullet in self.bullets:
            bullet.x += self.bullet_speed * self.dt
            if bullet.x > 800:
                self.bullets.remove(bullet)
                print("Bullet removed from the game, it went off-screen.")
            for zombie in self.zombies:
                if bullet.colliderect(zombie):
                    self.zombie_hit(zombie)
                    self.bullets.remove(bullet)
                    print(f"Bullet hit a zombie at {zombie.topleft}.")
                    self.kill_count += 1
                    self.score += 100
                    self.character.ammo += 1
                    if self.kill_count % 10 == 0:
                        self.character.ammo += 5
                        self.character.health += 5
                    print(f"Kill count: {self.kill_count}, Score: {self.score}, Ammo: {self.character.ammo}")
                    break

        zombie_count = 0
        print(f"Current zombie count: {zombie_count}")

    def update(self):
        # Update game state, handle logic, etc.
        self.dt = (pygame.time.get_ticks() - self.last_time) / 1000.0
        self.last_time = pygame.time.get_ticks()

        print(f"Delta time calculated: {self.dt:.2f} seconds.")
        self.handle_input()
        self.update_game_logic()
    def draw(self):
        # Draw game elements on the screen
        self.screen.fill((255, 255, 255))
        self.draw_game_elements()
    def draw_game_elements(self):
        # Draw the character, zombies, bullets, and UI elements
        pygame.draw.rect(self.screen, (0, 0, 255), self.character.hitbox)

        text = self.font.render(f"Health: {self.character.health}", True, (0, 0, 0))
        self.screen.blit(text, (10, 10))

        text = self.font.render(f"Ammo: {self.character.ammo}", True, (0, 0, 0))
        self.screen.blit(text, (10, 30))

        text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(text, (10, 50))

        text = self.font.render(f"Kills: {self.kill_count}", True, (0, 0, 0))
        self.screen.blit(text, (10, 70))

        for zombie in self.zombies:
            pygame.draw.rect(self.screen, (0, 255, 0), zombie)
        if self.character.hitbox_active:
            pygame.draw.rect(self.screen, self.character.hitbox_color, self.character.hitbox)
            pygame.draw.rect(self.screen, (0, 0, 0), self.character.hitbox, 1)
            pygame.draw.rect(self.screen, (255, 0, 0), self.character.hitbox, 2)

        pygame.draw.rect(self.screen, (80, 80, 80), (self.character.pos[0], self.character.pos[1], 50, 50))

        for bullet in self.bullets:
            pygame.draw.rect(self.screen, (255, 0, 0), bullet)
        if self.bullet_hitbox_active:
            pygame.draw.rect(self.screen, self.bullet_hitbox_color, self.bullet_hitbox)
            pygame.draw.rect(self.screen, (0, 0, 0), self.bullet_hitbox, 1)
            pygame.draw.rect(self.screen, (0, 255, 0), self.bullet_hitbox, 2)
        print("Game elements drawn on the screen.")
    
    def show_game_over_screen(self):
        self.screen.fill((0, 0, 0))
        game_over_text = self.endFont.render("Game Over", True, (255, 0, 0))
        score_text = self.endFont.render(f"Score: {self.score}", True, (255, 255, 255))
        rect = game_over_text.get_rect(center=(400, 250))
        self.screen.blit(game_over_text, rect.topleft)
        rect = score_text.get_rect(center=(400, 300))
        self.screen.blit(score_text, rect.topleft)

        if self.bullet_cooldown_timer < 0:
            ready_text = self.font.render("Ready To Shoot", True, (255, 255, 255))
            self.screen.blit(ready_text, self.character.pos)

        pygame.display.flip()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()
            time.sleep(0.1)
        
    def run(self):
        print("Game is running...")
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)
            
        self.show_game_over_screen()

if __name__ == "__main__":
    game = Game()
    game.run()