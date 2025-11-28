import sqlite3
from PIL import Image
from io import BytesIO
import math


COLORADO_BOUNDING_BOX = ( -124.41060660766607,32.5342307609976,-114.13445790587905,42.00965914828148)

DENVER_LAT = 39.7392
DENVER_LON = -104.9903

''' Max zoom is 13

'''


''' BASIC CLASS FUNCTION 

    get the center cordinates of the screen, and zoom level
    -> calculate if the col row off the center cordinates
        -> if the internal col row differ from the newly calcuated col row, output a new image, else return null 
    -> if the zoom changes, return a new screen else return null'''


class TileApp:
    def __init__(self, max_zoom = 13, min_zoom = 9):
        # iPhone window size
        self.iphone_width = 1170
        self.iphone_height = 2532
        '''1170 × 2532 pixels'''
        
        ''' *********** CLASS TOOLING ********** '''
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        
        self.default_zoom = min_zoom
        
        self.internal_col, self.internal_row = self.latlon_to_tile(DENVER_LAT,DENVER_LON,10)
        
        
        ''' ********** DATABASE TOOLING ********** '''
         # DATABASE
        self.comms = sqlite3.connect('satellite-2017-11-02_us_colorado.mbtiles')
        self.database_cursor = self.comms.cursor()
        
        
        
        
        
    # Fake main for testing 
    
    def start(self):
        """Runs after UI is built."""
        print("Starting app logic...")

        # DATABASE
        self.comms = sqlite3.connect('satellite-2017-11-02_us_colorado.mbtiles')
        self.database_cursor = self.comms.cursor()

        # Example tile fetch
        tile = self.get_tile_binary(0, 0, 0)
        
        # self.test_multi_tiles(self.get_tiles_where_zoom(3))
        
        # self.create_image_on_zoom(2)        
        
        # self.colorado_center_zoom(13)
        
        #self.create_image_on_zoom(6)
        
        # 6 7 8 dont work yet        
        self.colorado_center_radius(10)
        
        
    ''' Max number of tiles on screen possible 
        Each tile is 256x256
        
        iphone screen dim 1170 × 2532
        
        about 10 height and 5 wide full tiles with some screen crop
        
        Therefore from a given latitute and longitute:
            find the center tile calculate the top and bottom halfs, each half is 5 tiles wide and 5 tall,
            
            fill in two on either side
            
            total of 55 tiles
            
        This means that at certain zooms a full tile radius can be fetched
        
        therfore past zoom  3 a full tile PIXEL radius can be achieved
        
        full screen of tiles is 11 tiles tall by 5 tiles wide centered on a center tile
        
        
        
        Anything before needs to be filled
    '''
        

    ''' ******** Using TMS to adress tiles ********** '''

    def latlon_to_tile(self,lat, lon, zoom):
        n = 2 ** zoom

        # Column (X)
        tile_col = int((lon + 180.0) / 360.0 * n)

        # Row (Y) in XYZ scheme
        lat_rad = math.radians(lat)
        tile_row_xyz = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n)

        # Convert XYZ row → TMS/MBTiles row
        tile_row_mbtiles = (n - 1) - tile_row_xyz

        return tile_col, tile_row_mbtiles

        

    def get_tile_binary(self, col, row, zoom):
        self.database_cursor.execute(
            'SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?',
            (zoom, col, row)
        )
        return self.database_cursor.fetchone()
    
    def tile_to_png(self,data_binary, file_name):
        with open(file_name, 'wb') as f:
            f.write(data_binary)
    
    def get_tiles_where_zoom(self,zoom):
        self.database_cursor.execute(
            'SELECT tile_data FROM tiles WHERE zoom_level=?',
            (zoom,)
        )
        data_rows = self.database_cursor.fetchall()
        print(f"NUM TILES {len(data_rows)}")
        self.test_multi_tiles(data_rows)
        
        
        '''
        Used for streaming results instead of loading everything to memory
        
        cursor = self.database_cursor.execute("SELECT tile_data FROM tiles")

        for row in cursor:
            process(row)   # streamed one row at a time'''
        
        
    def create_image_on_zoom(self,zoom):        
        TILE_DIM = 256
        
        # Pull total tiles
        self.database_cursor.execute('SELECT count(tile_data) FROM tiles WHERE zoom_level=?',(zoom,))
        number_of_tiles = self.database_cursor.fetchone()
        root_tiles = int(math.sqrt(number_of_tiles[0]))
        print(f"N TILES: {number_of_tiles}  SQRT TILES: {root_tiles}")
        
        # Create stream cursor
        stream_cursor = self.database_cursor.execute('SELECT tile_data FROM tiles WHERE zoom_level=?',(zoom,))
        
        # Create image to paste to
        pil_img = Image.new('RGB',(TILE_DIM *root_tiles,TILE_DIM*root_tiles))
        
        # Image dimensions
        print(f"{TILE_DIM *root_tiles}x{TILE_DIM *root_tiles}")
        
        count = 0
        for data_blob in stream_cursor:
            image = Image.open(BytesIO(data_blob[0]))
            vertical_offset = int((count/root_tiles)) 
            horizontal_offset = root_tiles - 1 - (count%root_tiles) 
            pil_img.paste(image,(vertical_offset*TILE_DIM,horizontal_offset*TILE_DIM))
            count = count + 1
                
        pil_img.save('combined_image.png')
        
        
    
    def get_image_on_zoom(self,zoom):
        TILE_DIM = 256
        
        # Pull total tiles
        self.database_cursor.execute('SELECT count(tile_data) FROM tiles WHERE zoom_level=?',(zoom,))
        number_of_tiles = self.database_cursor.fetchone()
        root_tiles = int(math.sqrt(number_of_tiles[0]))
        print(f"N TILES: {number_of_tiles}  SQRT TILES: {root_tiles}")
        
        # Create stream cursor
        stream_cursor = self.database_cursor.execute('SELECT tile_data FROM tiles WHERE zoom_level=?',(zoom,))
        
        # Create image to paste to
        pil_img = Image.new('RGB',(TILE_DIM *root_tiles,TILE_DIM*root_tiles))
        
        # Image dimensions
        print(f"{TILE_DIM *root_tiles}x{TILE_DIM *root_tiles}")
        
        count = 0
        for data_blob in stream_cursor:
            image = Image.open(BytesIO(data_blob[0]))
            vertical_offset = int((count/root_tiles)) 
            horizontal_offset = root_tiles - 1 - (count%root_tiles) 
            pil_img.paste(image,(vertical_offset*TILE_DIM,horizontal_offset*TILE_DIM))
            count = count + 1
            
        
        return root_tiles * 256, root_tiles * 256, pil_img.tobytes()
    
    
    
    def get_image_square_bytes_no_tile_asm(self,zoom):
        # Each tile is a square 
        TILE_DIMENSION = 256
        
        # get the tile cordinate denver for now
        x,y = self.latlon_to_tile(DENVER_LAT,DENVER_LON,zoom)
        print(f"COLORADO CORDS {x} {y}")
        
        # Getting a square for now
        left_x = x - 2
        right_x = x + 2
        
        top_y = y - 2
        bottom_y = y + 2
        
        stream_cursor = self.database_cursor.execute("""SELECT tile_data FROM tiles 
                                        WHERE zoom_level = ? AND 
                                        tile_column BETWEEN ? AND ? 
                                        AND tile_row BETWEEN ? AND ?
                                        ORDER BY tile_row DESC, tile_column ASC;""",
                                        (zoom, (left_x),(right_x),(top_y),(bottom_y))
                                        )
        image_byte_arr = bytearray()
        for data in stream_cursor:
            image_byte_arr += data[0]
            
        image_square = 4
            
        return image_square*TILE_DIMENSION, image_square*TILE_DIMENSION, image_byte_arr
        
    
    
    
    def get_image_square_bytes_on_zoom(self,zoom):
        # At zooms 6 7 8 starts looking at colorado only
        '''sqlite> SELECT count(*) from tiles WHERE zoom_level = 6;
        4
        sqlite> SELECT count(*) from tiles WHERE zoom_level = 7;
        9
        sqlite> SELECT count(*) from tiles WHERE zoom_level = 8;
        30
        
        '''
        
        DISPLAYED_TILE_SIZE = 256
        
        # Check number of tiles 
        self.database_cursor.execute('SELECT count(*) from tiles WHERE zoom_level = ?;',(zoom,))
        num_tiles = self.database_cursor.fetchone()
        print(f"Number of tiles {num_tiles[0]}")
        if num_tiles[0] < DISPLAYED_TILE_SIZE:
            #fetch all tiles and display
            pass
        
        TILE_DIM = 256
        
        x,y = self.latlon_to_tile(DENVER_LAT,DENVER_LON,zoom)
        print(f"COLORADO CORDS {x} {y}")
        
        
        # Consider pulling tiles to wrap around the world in the case less than expected is fetched using between
        
        
        image_width = 8
        image_height = 8
        
        left_x = x - 4
        right_x = x + 3
        
        top_y = y - 4
        bottom_y = y + 3
        
        # check for number of cutout tiles
        coutout_num_tiles = self.database_cursor.execute("""SELECT count(tile_data) FROM tiles 
                                        WHERE zoom_level = ? AND 
                                        tile_column BETWEEN ? AND ? 
                                        AND tile_row BETWEEN ? AND ?;""",
                                        (zoom, (left_x),(right_x),(top_y),(bottom_y))
                                        ).fetchone()
        
        print(f"Number of cutout tiles {coutout_num_tiles[0]}")
      
        stream_cursor = self.database_cursor.execute("""SELECT tile_data FROM tiles 
                                        WHERE zoom_level = ? AND 
                                        tile_column BETWEEN ? AND ? 
                                        AND tile_row BETWEEN ? AND ?
                                        ORDER BY tile_row DESC, tile_column ASC;""",
                                        (zoom, (left_x),(right_x),(top_y),(bottom_y))
                                        )
        
        
        
        # Create image to paste to
        pil_img = Image.new('RGB',(TILE_DIM *image_width,TILE_DIM*image_height))
        
        # Image dimensions
        print(f"{TILE_DIM *image_width}x{TILE_DIM *image_height}")
        
        count = 0
        for data in stream_cursor:
            image = Image.open(BytesIO(data[0]))            
            vertical_offset = (count // image_width) * TILE_DIM
            horizontal_offset = (count % image_width) * TILE_DIM
            pil_img.paste(image,(horizontal_offset,vertical_offset))
            print(f"image pastings {horizontal_offset} {vertical_offset}")
            count = count + 1
                
        #pil_img.save('cutout_image.png')
        pil_img = pil_img.convert("RGBA")

        return image_width*TILE_DIM, image_height*TILE_DIM, pil_img.tobytes()
        
    ''' 2**0 = 1
        2**1 = 2
        2**2 = 4
        2**3 = 8
        2**4 = 16
        2**5 = 32
        2**6 = 64
        2**7 = 128
        2**8 = 256
        2**9 = 512
        2**10 = 1024
        2**11 = 2048
        2**12 = 4096
        2**13 = 8192
        2**14 = 16384'''
       
            
        
    def colorado_center_zoom(self,zoom):
        # Get tile cordintes
        x, y = self.latlon_to_tile(DENVER_LAT,DENVER_LON,zoom)
        print(f'TILE CORDS {x} {y}')
        center_tile = self.get_tile_binary(x,y,zoom)
        if center_tile:
            self.tile_to_png(center_tile[0],'tile.png')
        else:
            print('Tile doesnt exist')
            
    '''
        Center of denver cords tile cords 1706 5082
        
        
    '''
            
            
    def colorado_center_radius(self,zoom):
        # At zooms 6 7 8 starts looking at colorado only
        '''sqlite> SELECT count(*) from tiles WHERE zoom_level = 6;
        4
        sqlite> SELECT count(*) from tiles WHERE zoom_level = 7;
        9
        sqlite> SELECT count(*) from tiles WHERE zoom_level = 8;
        30
        
        '''
        
        DISPLAYED_TILE_SIZE = 55
        
        # Check number of tiles 
        self.database_cursor.execute('SELECT count(*) from tiles WHERE zoom_level = ?;',(zoom,))
        num_tiles = self.database_cursor.fetchone()
        print(f"Number of tiles {num_tiles[0]}")
        if num_tiles[0] < DISPLAYED_TILE_SIZE:
            #fetch all tiles and display
            pass
        
        TILE_DIM = 256
        
        x,y = self.latlon_to_tile(DENVER_LAT,DENVER_LON,zoom)
        print(f"COLORADO CORDS {x} {y}")
        
        
        # Consider pulling tiles to wrap around the world in the case less than expected is fetched using between
        
        left_x = x - 2
        right_x = x + 2
        
        top_y = y - 5
        bottom_y = y + 5
        
        # check for number of cutout tiles
        coutout_num_tiles = self.database_cursor.execute("""SELECT count(tile_data) FROM tiles 
                                        WHERE zoom_level = ? AND 
                                        tile_column BETWEEN ? AND ? 
                                        AND tile_row BETWEEN ? AND ?;""",
                                        (zoom, (left_x),(right_x),(top_y),(bottom_y))
                                        ).fetchone()
        
        print(f"Number of cutout tiles {coutout_num_tiles[0]}")
      
        stream_cursor = self.database_cursor.execute("""SELECT tile_data FROM tiles 
                                        WHERE zoom_level = ? AND 
                                        tile_column BETWEEN ? AND ? 
                                        AND tile_row BETWEEN ? AND ?
                                        ORDER BY tile_row DESC, tile_column ASC;""",
                                        (zoom, (left_x),(right_x),(top_y),(bottom_y))
                                        )
        
        image_width = 5
        image_height = 11
        
        # Create image to paste to
        pil_img = Image.new('RGB',(TILE_DIM *5,TILE_DIM*11))
        
        # Image dimensions
        print(f"{TILE_DIM *image_width}x{TILE_DIM *image_height}")
        
        count = 0
        for data in stream_cursor:
            image = Image.open(BytesIO(data[0]))
            vertical_offset = int((count/image_width)) 
            horizontal_offset =   (count%image_width) 
            pil_img.paste(image,(horizontal_offset*TILE_DIM,vertical_offset*TILE_DIM))
            print(f"image pastings {horizontal_offset} {vertical_offset}")
            count = count + 1
                
        pil_img.save('cutout_image.png')
            
    
    
    def get_screen(self,zoom,lat,lon):
        pass
        
        
    
    
    '''
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 1;
    4
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 2;
    16
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 3;
    64
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 4;
    256
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 5;
    1024
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 6;
    4
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 7;
    9
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 8;
    30
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 9;
    99
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 10;
    336
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 11;
    1271
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 12;
    4800
    sqlite> SELECT count(*) from tiles WHERE zoom_level = 14;
    0
    sqlite> 
    '''

            
        
                
           
                
           
                    
                
    


''' TILE DOCUMENTATION 

    Colorado Bounding box
    -124.41060660766607,32.5342307609976,-114.13445790587905,42.00965914828148

    (0,0) is top-left of the world
    
    At zoom Z:

        num_tiles = 2^Z
        X range: 0 → num_tiles - 1
        Y range: 0 → num_tiles - 1
    
'''

'''from PIL import Image

# Load images
image1 = Image.open('image1.jpg')
image2 = Image.open('image2.jpg')

# Horizontal Concatenation
# Create a new image with the combined width and the maximum height.
combined_width_h = image1.width + image2.width
combined_height_h = max(image1.height, image2.height)
horizontally_combined_pil = Image.new('RGB', (combined_width_h, combined_height_h))

# Paste images
horizontally_combined_pil.paste(image1, (0, 0))
horizontally_combined_pil.paste(image2, (image1.width, 0))
horizontally_combined_pil.save('horizontally_combined_pil.jpg')

# Vertical Concatenation
# Create a new image with the maximum width and the combined height.
combined_width_v = max(image1.width, image2.width)
combined_height_v = image1.height + image2.height
vertically_combined_pil = Image.new('RGB', (combined_width_v, combined_height_v))

# Paste images
vertically_combined_pil.paste(image1, (0, 0))
vertically_combined_pil.paste(image2, (0, image1.height))
vertically_combined_pil.save('vertically_combined_pil.jpg')'''
if __name__ == "__main__":
    app = TileApp()

'''def save_binary_as_png(raw_binary):
    with open("tile.png", "wb") as f:
        f.write(raw_binary)
'''