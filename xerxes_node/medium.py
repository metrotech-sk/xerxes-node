#!/usr/bin/env python3
# -*- coding: utf-8 -*-


_g = 9.80665


class Medium:
    @staticmethod
    def ethyleneglycol(Pa):
        return Pa/(_g*1.1132)

    @staticmethod
    def water(Pa):
        return Pa/(_g*1)

    @staticmethod
    def siloxane(Pa):
        return Pa/(_g*0.965)
    
    @staticmethod        
    def propyleneglycol(Pa):
        return Pa/(_g*1.04)