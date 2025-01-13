import itertools
from tqdm import tqdm
def denormalize_s_expr_new(normed_expr,
                           entity_label_map,
                           type_label_map,
                           surface_index):
    expr = normed_expr

    convert_map = {
        '( greater equal': '( ge',
        '( greater than': '( gt',
        '( less equal': '( le',
        '( less than': '( lt'
    }

    for k in convert_map:
        expr = expr.replace(k, convert_map[k])
        expr = expr.replace(k.upper(), convert_map[k])

    # expr = expr.replace(', ',' , ')
    tokens = expr.split(' ')

    segments = []
    prev_left_bracket = False
    prev_left_par = False
    cur_seg = ''

    for t in tokens:

        if t == '[':
            prev_left_bracket = True
            if cur_seg:
                segments.append(cur_seg)
        elif t == ']':
            prev_left_bracket = False
            cur_seg = cur_seg.strip()

            # find in linear origin map
            processed = False

            if not processed:
                if cur_seg.lower() in type_label_map:  # type
                    cur_seg = type_label_map[cur_seg.lower()]
                    processed = True
                else:  # relation or unlinked entity
                    if ' , ' in cur_seg:
                        if is_number(cur_seg):
                            # check if it is a number
                            cur_seg = cur_seg.replace(" , ", ".")
                            cur_seg = cur_seg.replace(" ,", ".")
                            cur_seg = cur_seg.replace(", ", ".")
                        else:
                            # view as relation
                            cur_seg = cur_seg.replace(' , ', ',')
                            cur_seg = cur_seg.replace(',', '.')
                            cur_seg = cur_seg.replace(' ', '_')
                        processed = True
                    else:
                        search = True
                        if is_number(cur_seg):
                            search = False
                            cur_seg = cur_seg.replace(" , ", ".")
                            cur_seg = cur_seg.replace(" ,", ".")
                            cur_seg = cur_seg.replace(", ", ".")
                            cur_seg = cur_seg.replace(",", "")
                        elif len(entity_label_map.keys()) != 0:
                            search = False
                            if cur_seg.lower() in entity_label_map:
                                cur_seg = entity_label_map[cur_seg.lower()]
                            else:
                                similarities = model.similarity([cur_seg.lower()], list(entity_label_map.keys()))
                                merged_list = list(zip([v for _, v in entity_label_map.items()], similarities[0]))
                                sorted_list = sorted(merged_list, key=lambda x: x[1], reverse=True)[0]
                                if sorted_list[1] > 0.2:
                                    cur_seg = sorted_list[0]
                                else:
                                    search = True
                        if search:
                            facc1_cand_entities = surface_index.get_indexrange_entity_el_pro_one_mention(cur_seg,
                                                                                                         top_k=50)
                            if facc1_cand_entities:
                                temp = []
                                for key in list(facc1_cand_entities.keys())[1:]:
                                    if facc1_cand_entities[key] >= 0.001:
                                        temp.append(key)
                                if len(temp) > 0:
                                    cur_seg = [list(facc1_cand_entities.keys())[0]] + temp
                                else:
                                    cur_seg = list(facc1_cand_entities.keys())[0]

            segments.append(cur_seg)
            cur_seg = ''
        else:
            if prev_left_bracket:
                # in a bracket
                cur_seg = cur_seg + ' ' + t
            else:
                if t == '(':
                    prev_left_par = True
                    segments.append(t)
                else:
                    if prev_left_par:
                        if t in ['ge', 'gt', 'le', 'lt']:  # [ge, gt, le, lt] lowercase
                            segments.append(t)
                        else:
                            segments.append(t.upper())  # [and, join, r, argmax, count] upper case
                        prev_left_par = False
                    else:
                        if t != ')':
                            if t.lower() in entity_label_map:
                                t = entity_label_map[t.lower()]
                            else:
                                t = type_checker(t)  # number
                        segments.append(t)

    combinations = [list(comb) for comb in itertools.islice(
        itertools.product(*[item if isinstance(item, list) else [item] for item in segments]), 10000)]

    exprs = [" ".join(s) for s in combinations]

    return exprs
def execute_normed_s_expr_from_label_maps_rel(normed_expr,
                                              entity_label_map,
                                              type_label_map,
                                              surface_index
                                              ):
    try:
        denorm_sexprs = denormalize_s_expr_new(normed_expr,
                                               entity_label_map,
                                               type_label_map,
                                               surface_index
                                               )
    except:
        return 'null', []

    query_exprs = [d.replace('( ', '(').replace(' )', ')') for d in denorm_sexprs]

    for d in tqdm(denorm_sexprs[:50]):
        query_expr, denotation = try_relation(d)
        if len(denotation) != 0:
            break

    if len(denotation) == 0:
        query_expr = query_exprs[0]

    return query_expr, denotation
def try_relation(d):  #
    ent_list = set()
    rel_list = set()
    denorm_sexpr = d.split(' ')
    for item in denorm_sexpr:
        if item.startswith('m.'):
            ent_list.add(item)
        elif '.' in item:
            rel_list.add(item)
    ent_list = list(ent_list)
    rel_list = list(rel_list)
    cand_rels = set()
    print(f"ent_list:{ent_list}\nrel_list:{rel_list}\ncand_rels:{cand_rels}")
    # for ent in ent_list:
    #     in_rels, out_rels, _ = get_2hop_relations_with_odbc_wo_filter(ent)
    #     cand_rels = cand_rels | set(in_rels) | set(out_rels)
    # cand_rels = list(cand_rels)
    # if len(cand_rels) == 0 or len(rel_list) == 0:
    #     return d.replace('( ', '(').replace(' )', ')'), []
    # similarities = model.similarity(rel_list, cand_rels)
    # change = dict()
    # for i, rel in enumerate(rel_list):
    #     merged_list = list(zip(cand_rels, similarities[i]))
    #     sorted_list = sorted(merged_list, key=lambda x: x[1], reverse=True)
    #     change_rel = []
    #     for s in sorted_list:
    #         if s[1] > 0.01:
    #             change_rel.append(s[0])
    #     change[rel] = change_rel[:15]
    # for i, item in enumerate(denorm_sexpr):
    #     if item in rel_list:
    #         denorm_sexpr[i] = change[item]
    # combinations = [list(comb) for comb in itertools.islice(
    #     itertools.product(*[item if isinstance(item, list) else [item] for item in denorm_sexpr]), 10000)]
    # exprs = [" ".join(s) for s in combinations][:4000]
    # query_exprs = [d.replace('( ', '(').replace(' )', ')') for d in exprs]
    # for query_expr in query_exprs:
    #     try:
    #         # invalid sexprs, may leads to infinite loops
    #         if 'OR' in query_expr or 'WITH' in query_expr or 'PLUS' in query_expr:
    #             denotation = []
    #         else:
    #             sparql_query = lisp_to_sparql(query_expr)
    #             denotation = execute_query_with_odbc(sparql_query)
    #             denotation = [res.replace("http://rdf.freebase.com/ns/", '') for res in denotation]
    #             if len(denotation) == 0:
    #
    #                 ents = set()
    #
    #                 for item in sparql_query.replace('(', ' ( ').replace(')', ' ) ').split(' '):
    #                     if item.startswith("ns:m."):
    #                         ents.add(item)
    #                 addline = []
    #                 for i, ent in enumerate(list(ents)):
    #                     addline.append(f'{ent} rdfs:label ?en{i} . ')
    #                     addline.append(f'?ei{i} rdfs:label ?en{i} . ')
    #                     addline.append(f'FILTER (langMatches( lang(?en{i}), "EN" ) )')
    #                     sparql_query = sparql_query.replace(ent, f'?ei{i}')
    #                 clauses = sparql_query.split('\n')
    #                 for i, line in enumerate(clauses):
    #                     if line == "FILTER (!isLiteral(?x) OR lang(?x) = '' OR langMatches(lang(?x), 'en'))":
    #                         clauses = clauses[:i + 1] + addline + clauses[i + 1:]
    #                         break
    #                 sparql_query = '\n'.join(clauses)
    #                 denotation = execute_query_with_odbc(sparql_query)
    #                 denotation = [res.replace("http://rdf.freebase.com/ns/", '') for res in denotation]
    #     except:
    #         denotation = []
    #     if len(denotation) != 0:
    #         break
    # if len(denotation) == 0:
    #     query_expr = query_exprs[0]
    # return query_expr, denotation


if __name__ == '__main__':
    logil_form="( JOIN ( R [ location, country, languages spoken ] ) [ Jamaica ] )"
    try_relation(logil_form)