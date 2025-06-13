from settings import *
from weapons import Pistol, Shotgun, Sword, AutoRifle
from sprites import Gun


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, enemy_sprites):
        super().__init__(groups)
        self.load_images()
        self.state, self.frame_index = 'right', 0
        self.image = pygame.image.load(join('..', 'images', 'player', 'down', '0.png')).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)
        self.enemy_sprites = enemy_sprites

        # stats
        self.health = 1000
        self.alive = True
        self.death_time = 0

        # movement
        self.direction = pygame.Vector2()
        self.speed = 500
        self.collision_sprites = collision_sprites

        # weapon system
        self.bullet_sprites = pygame.sprite.Group()  # Создаем группу для пуль
        self.weapons = [
            Pistol(self, {'all': groups, 'bullet': self.bullet_sprites}),
            Shotgun(self, {'all': groups, 'bullet': self.bullet_sprites}),
            AutoRifle(self, {'all': groups, 'bullet': self.bullet_sprites})
        ]
        self.current_weapon_index = 0
        self.current_weapon = self.weapons[self.current_weapon_index]
        
        # Создаем визуальное представление оружия
        self.gun = Gun(self, groups)

    def load_images(self):
        self.frames = {'left': [], 'right': [], 'up': [], 'down': []}

        for state in self.frames.keys():
            for folder_path, sub_folders, file_names in walk(join('..', 'images', 'player', state)):
                if file_names:
                    for file_name in sorted(file_names, key=lambda name: int(name.split('.')[0])):
                        full_path = join(folder_path, file_name)
                        surf = pygame.image.load(full_path).convert_alpha()
                        self.frames[state].append(surf)

    def switch_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self.current_weapon_index = index
            self.current_weapon = self.weapons[self.current_weapon_index]
            # Обновляем изображение оружия
            self.gun.image = self.current_weapon.weapon_surf

    def input(self):
        if not self.alive:
            return

        keys = pygame.key.get_pressed()
        
        # Movement
        self.direction.x = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.direction.y = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        self.direction = self.direction.normalize() if self.direction else self.direction

        # Weapon switching
        if keys[pygame.K_1]:
            self.switch_weapon(0)
        elif keys[pygame.K_2]:
            self.switch_weapon(1)
        elif keys[pygame.K_3]:
            self.switch_weapon(2)

        # Shooting
        if pygame.mouse.get_pressed()[0]:
            self.current_weapon.shoot()

    def get_weapon_direction(self):
        mouse_pos = pygame.mouse.get_pos()
        screen_center = pygame.math.Vector2(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        return (pygame.math.Vector2(mouse_pos) - screen_center).normalize()

    def move(self, dt):
        if not self.alive:
            return

        # Сохраняем старую позицию для возможного отката
        old_x = self.hitbox_rect.x
        old_y = self.hitbox_rect.y

        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')
        self.rect.center = self.hitbox_rect.center

    def check_death(self):
        if self.health <= 0 and self.alive:
            self.alive = False
            self.death_time = pygame.time.get_ticks()

    def collision(self, direction):
        # Коллизия с окружением
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                else:
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top

        # Коллизия с врагами - игрок не может их сдвинуть
        for enemy in self.enemy_sprites:
            if enemy.death_time == 0 and enemy.hitbox_rect.colliderect(self.hitbox_rect):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox_rect.right = enemy.hitbox_rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = enemy.hitbox_rect.right
                else:
                    if self.direction.y < 0:
                        self.hitbox_rect.top = enemy.hitbox_rect.bottom
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = enemy.hitbox_rect.top

    def animate(self, dt):
        if not self.alive:
            return

        # get state
        if self.direction.x != 0:
            self.state = 'right' if self.direction.x > 0 else 'left'
        if self.direction.y != 0:
            self.state = 'down' if self.direction.y > 0 else 'up'

        # animate
        self.frame_index = self.frame_index + 5 * dt if self.direction else 0
        self.image = self.frames[self.state][int(self.frame_index) % len(self.frames[self.state])]

    def update(self, dt):
        # input
        self.input()
        
        # update bullet sprites
        self.bullet_sprites.update(dt)
        
        # collision
        self.move(dt)
        self.bullet_collision()  # Проверяем коллизии пуль
        self.check_death()

        # Update weapon
        if self.alive:
            weapon_dir = self.get_weapon_direction()
            self.current_weapon.update_position(pygame.math.Vector2(self.rect.center), weapon_dir)
            self.current_weapon.update_timer(self.current_weapon.cooldown)

    def draw_hitbox(self, surface, offset):
        rect_with_offset = self.hitbox_rect.copy()
        rect_with_offset.topleft += offset
        pygame.draw.rect(surface, (255, 0, 0), rect_with_offset, 2)

    def bullet_collision(self):
        # Проверяем коллизии для каждой пули
        for bullet in self.bullet_sprites.sprites():
            # Проверяем коллизии с врагами
            for enemy in self.enemy_sprites.sprites():
                if enemy.check_bullet_collision(bullet):
                    # Определяем тип оружия и урон
                    weapon_damage = {
                        'pistol': 15,  # 2 выстрела для убийства (30 HP / 15 = 2)
                        'drobovik': 10,  # 3 пули по 10 урона каждая
                        'avtomat': 12   # Быстрая стрельба, но меньше урон
                    }.get(self.current_weapon, 15)
                    
                    print(f"Попадание из {self.current_weapon}, урон: {weapon_damage}")  # Для отладки
                    
                    # Наносим урон врагу
                    enemy.take_damage(weapon_damage)
                    
                    # Удаляем пулю только для пистолета и автомата
                    if self.current_weapon != 'drobovik':
                        bullet.kill()
                    break  # Прерываем проверку для этой пули, если попали во врага