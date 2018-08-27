# -*- coding: utf-8 -*-

import requests
import time
import json
import pickle
import pandas as pd


def get_url(product_id, page):
    """
    根据商品ID和页面数，得到URL
    :param product_id: 商品ID
    :param page: 页面数
    :return: 需要爬取的评论URL
    """
    url1 = 'http://sclub.jd.com/comment/productPageComments.action?productId='
    url2 = '&score=0&sortType=3&page='
    url3 = '&pageSize=10&isShadowSku=0&rid=0&fold=1'
    sent = url1+str(product_id)+url2+str(page)+url3
    return sent


def get_page_information(url):
    """
    通过url进行request，从而获取页面信息
    :param url: 目标url
    :return: json文件
    """
    ret = requests.get(url)
    s1 = ret.text
    data = json.loads(s1, encoding='gbk')
    print(data)
    return data


def get_comments(data):
    """
    根据json文件得到评论，并确定是否有附加评论
    :param data: json文件
    :return: 评论以及附加评论
    """
    comments_list = data.get('comments', [])
    all_list = []
    for comment in comments_list:
        one_list=[]
        one_list.append(comment.get('id', ''))
        one_list.append(comment.get('referenceId', ''))
        one_list.append(comment.get('referenceName', ''))
        one_list.append(comment.get('score', ''))
        one_list.append(comment.get('content', ''))
        if comment.get('afterUserComment', None):
            one_list.append(comment.get('afterUserComment', None).get('hAfterUserComment').get('content', ''))
        all_list.append(one_list)
        print(all_list)
    return all_list


def get_pages_details(product_id):
    """
    获取最大页面之内的评论
    :param product_id:商品ID
    :return:
    """
    error_count = 0
    while(1):
        time.sleep(2)
        try:
            first_url = get_url(product_id, 0)
            first_page_data = get_page_information(first_url)
            break
        except:
            if error_count > 50:
                print('第一个页面无法访问')
                break
            print("访问失败")
            error_count += 1
    #找到最大页码
    total_pages = first_page_data.get('maxPage', 1) if first_page_data.get('maxPage', 1) < MAX_PAGE else MAX_PAGE
    print("最大页码(404就是没找到):", total_pages)
    all_page_comments = []
    for page_number in range(0, total_pages):
        error_count = 0
        while(1):
            time.sleep(2)
            try:
                target_url = get_url(product_id, page_number)
                data = get_page_information(target_url)
                one_page_comment = get_comments(data)
                all_page_comments.extend(one_page_comment)
                print(page_number)
                break
            except Exception as e:
                error_count += 1
                if error_count >= 10:
                    print('页面访问或者解析出现问题')
                    break
                proxy_use_count=0
                print(e, file=err)
                continue
    print(all_page_comments)
    return all_page_comments


def save_comments(all_need, file_name):
    """
    保存
    :param all_need:
    :param file_name:
    :return:
    """
    sent = file_name+'.p'
    print(sent)
    sent2 = file_name+'.xlsx'
    print(sent2)
    with open(str(sent), 'wb') as out_file:
        pickle.dump(all_need, out_file)
    data_f = pd.DataFrame(all_need)
    data_f.to_excel(sent2)
    print("文件已保存")


if __name__ == '__main__':
    MAX_PAGE = 404
    err = open('err.log', 'w')
    all = get_pages_details(product_id=6333842)
    print("获得评论数", len(all))
    #下面的保存的名字，生产两个文件.p .xlsx
    save_comments(all, r"D:\京东京东")
    err.close()
