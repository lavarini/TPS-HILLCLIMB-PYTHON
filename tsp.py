#!/usr/bin/python

import random
import sys
import getopt
from PIL import Image, ImageDraw, ImageFont
from math import sqrt

def rand_seq(size):
    '''generates values in random order
    equivalent to using shuffle in random,
    without generating all values at once'''
    values=range(size)
    for i in xrange(size):
        # pick a random index into remaining values
        j=i+int(random.random()*(size-i))
        # swap the values
        values[j],values[i]=values[i],values[j]
        # return the swapped value
        yield values[i] 

def all_pairs(size):
    '''generates all i,j pairs for i,j from 0-size'''
    for i in rand_seq(size):
        for j in rand_seq(size):
            yield (i,j)

def reversed_sections(tour):
    '''generator to return all possible variations where the section between two cities are swapped'''
    for i,j in all_pairs(len(tour)):
        if i != j:
            copy=list(tour)
            if i < j:
                copy[i:j+1]=reversed(tour[i:j+1])
            else:
                copy[i+1:]=reversed(tour[:j])
                copy[:j]=reversed(tour[i+1:])
            copy=tuple(copy)
            if copy != tour: # no point returning the same tour
                yield copy

def swapped_cities(tour):
    '''generator to create all possible variations where two cities have been swapped'''
    for i,j in all_pairs(len(tour)):
        if i < j:
            copy=list(tour)
            copy[i],copy[j]=tour[j],tour[i]
            yield tuple(copy)

def edges(tour):
    tour_len=len(tour)
    for i in xrange(tour_len):
        a,b=tour[i],tour[(i+1)%tour_len]
        if a > b:
            a,b=b,a
        yield (a,b)

def _add_route_choices(tour, routes_choices):
    for a, b in edges(tour):
        # from a can got to b and vice-versa
        routes_choices[a].add(b)
        routes_choices[b].add(a)

def calc_route_choices(tour1, tour2):
    routes_choices = [set() for i in tour1]
    _add_route_choices(tour1, routes_choices)
    _add_route_choices(tour2, routes_choices)
    return routes_choices

def recombine(tour1,tour2):
    '''
    combine two parent routes
    to create a new route that only has edges that appear
    in one or both parents
    '''
    routes_choices=calc_route_choices(tour1, tour2)
    return find_common_route(routes_choices, tour1)

def find_common_route(routes_choices, tour1):
    current=random.choice(tour1) # random starting city
    tour=[current]
    chosen=set(tour)
    while len(tour) != len(tour1):
        # find out what our options are
        next=choose_next_neighbour(routes_choices, chosen, current)
        if next is None:
            # no obvious neighbours, so just choose one
            # from the other remaining cities
            possible=set(tour1)-chosen
            next=random.choice(list(possible))
        current=next
        tour.append(current)
        chosen.add(current)
            
    return tuple(tour1)

def choose_next_neighbour(routes_choices, chosen, city):
    neighbours=list(routes_choices[city]-chosen)
    if len(neighbours):
        random.shuffle(neighbours)
        count, neighbour=min((len(routes_choices[n]), n) for n in neighbours)
        return neighbour
    return None

def cartesian_matrix(coords):
    '''create a distance matrix for the city coords that uses straight line distance'''
    matrix={}
    for i,(x1,y1) in enumerate(coords):
        for j,(x2,y2) in enumerate(coords):
            dx,dy=x1-x2,y1-y2
            dist=sqrt(dx*dx + dy*dy)
            matrix[i,j]=dist
    return matrix

def read_coords(coord_file):
    '''
    read the coordinates from file and return the distance matrix.
    coords should be stored as comma separated floats, one x,y pair per line.
    '''
    coords=[]
    for line, str in enumerate(coord_file):
        if line > 5 and str.find('EOF') == -1:
            a,x,y=str.strip().split(' ')
            coords.append((float(x),float(y)))
    return coords

def tour_length(matrix,tour):
    '''total up the total length of the tour based on the distance matrix'''
    total=0
    num_cities=len(tour)
    for i in range(num_cities):
        j=(i+1)%num_cities
        city_i=tour[i]
        city_j=tour[j]
        total+=matrix[city_i,city_j]
    return total

def write_tour_to_img(coords,tour,title,img_file):
    padding=20
    # shift all coords in a bit
    coords=[(x+padding,y+padding) for (x,y) in coords]
    maxx,maxy=0,0
    for x,y in coords:
        maxx=max(x,maxx)
        maxy=max(y,maxy)
    maxx+=padding
    maxy+=padding
    img=Image.new("RGB",(int(maxx),int(maxy)),color=(255,255,255))
    
    font=ImageFont.load_default()
    d=ImageDraw.Draw(img);
    num_cities=len(tour)
    for i in range(num_cities):
        j=(i+1)%num_cities
        city_i=tour[i]
        city_j=tour[j]
        x1,y1=coords[city_i]
        x2,y2=coords[city_j]
        d.line((int(x1),int(y1),int(x2),int(y2)),fill=(0,0,0))
        d.text((int(x1)+7,int(y1)-5),str(i),font=font,fill=(32,32,32))
    
    
    for x,y in coords:
        x,y=int(x),int(y)
        d.ellipse((x-5,y-5,x+5,y+5),outline=(0,0,0),fill=(196,196,196))
    
    d.text((1,1),title,font=font,fill=(0,0,0))
    
    del d
    img.save(img_file, "PNG")

def init_random_tour(tour_length):
   tour=range(tour_length)
   random.shuffle(tour)
   return tuple(tour)

def run_hillclimb(init_function,move_operator,objective_function,max_iterations):
    from hillclimb import hillclimb_and_restart
    iterations,score,best=hillclimb_and_restart(init_function,move_operator,objective_function,max_iterations)
    return iterations,score,best

def run_anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha):
    if start_temp is None or alpha is None:
        usage();
        print "missing --cooling start_temp:alpha for annealing"
        sys.exit(1)
    from sa import anneal
    iterations,score,best=anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha)
    return iterations,score,best

def run_evolve(init_function,move_operator,objective_function,max_iterations,pop_size,tournament_size):
    if pop_size is None:
        usage();
        print "missing --popsize size for evolve"
        sys.exit(1)
    from ga import evolve
    iterations,score,best=evolve(init_function,move_operator,objective_function,max_iterations,recombine,pop_size,tournament_size)
    return iterations,score,best

def usage():
    print "usage: python %s [-o <output image file>] [-v] [-m reversed_sections|swapped_cities] -n <max iterations> [-a hillclimb|anneal] [--cooling start_temp:alpha] <city file>" % sys.argv[0]

def main():
    try:
        options, args = getopt.getopt(sys.argv[1:], "ho:vm:n:a:", ["cooling=","popsize=","tournament="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    out_file_name=None
    max_iterations=None
    verbose=None
    move_operator=reversed_sections
    run_algorithm=run_hillclimb
    
    start_temp,alpha=None,None
    
    pop_size=None
    tournament_size=2
    
    for option,arg in options:
        if option == '-v':
            verbose=True
        elif option == '-h':
            usage()
            sys.exit()
        elif option == '-o':
            out_file_name=arg
        elif option == '-n':
            max_iterations=int(arg)
        elif option == '-m':
            if arg == 'swapped_cities':
                move_operator=swapped_cities
            elif arg == 'reversed_sections':
                move_operator=reversed_sections
        elif option == '-a':
            if arg == 'hillclimb':
                run_algorithm=run_hillclimb
            elif arg == 'anneal':
                # do this to pass start_temp and alpha to run_anneal
                def run_anneal_with_temp(init_function,move_operator,objective_function,max_iterations):
                    return run_anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha)
                run_algorithm=run_anneal_with_temp
            elif arg == 'evolve':
                def run_evolve_with_pop_size(init_function,move_operator,objective_function,max_iterations):
                    return run_evolve(init_function,move_operator,objective_function,max_iterations,pop_size,tournament_size)
                run_algorithm=run_evolve_with_pop_size
        elif option == '--cooling':
            start_temp,alpha=arg.split(':')
            start_temp,alpha=float(start_temp),float(alpha)
        elif option == '--popsize':
            pop_size=int(arg)
        elif option == '--tournament':
            tournament_size=int(arg)
    
    if max_iterations is None:
        usage();
        sys.exit(2)
    
    if out_file_name and not out_file_name.endswith(".png"):
        usage()
        print "output image file name must end in .png"
        sys.exit(1)
    
    if len(args) != 1:
        usage()
        print "no city file specified"
        sys.exit(1)
    
    city_file=args[0]
    
    # enable more verbose logging (if required) so we can see workings
    # of the algorithms
    import logging
    format='%(asctime)s %(levelname)s %(message)s'
    if verbose:
        logging.basicConfig(level=logging.INFO,format=format)
    else:
        logging.basicConfig(format=format)
    
    # setup the things tsp specific parts hillclimb needs
    coords=read_coords(file(city_file))
    init_function=lambda: init_random_tour(len(coords))
    matrix=cartesian_matrix(coords)
    objective_function=lambda tour: -tour_length(matrix,tour)
    
    logging.info('using move_operator: %s'%move_operator)
    
    iterations,score,best=run_algorithm(init_function,move_operator,objective_function,max_iterations)
    # output results
    print iterations,score,best
    
    if out_file_name:
        write_tour_to_img(coords,best,'%s: %f'%(city_file,score),file(out_file_name,'w'))

if __name__ == "__main__":
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    main()