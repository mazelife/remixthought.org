String.prototype.interpolate = function(data){
	
	var type = function(obj, cmp){
		var type = obj.constructor.toString().match(/function ([A-Za-z]+)\(\)/)[1];
		if(typeof cmp == 'undefined') return type;
		return type.toLowerCase() == cmp.toLowerCase();
	}
	
	var doInterpolation = function(string, find, replace, replType, global){
		
		if(typeof global == 'undefined') var global = false;
		
		switch(replType){
			case 's':
				if(!type(replace, 'string')) throw('%s format: a string is required')
				replaceWith = String(replace);
				break;
			case 'i':
				if(!type(replace, 'number')) throw('%i format: a number is required')
				replaceWith = parseInt(replace);
				break;
			case 'f':
				if(!type(replace, 'number')) throw('%f format: a number is required')
				replaceWith = parseFloat(replace);
				break;
			case 'n':
				if(!type(replace, 'number')) throw('%n format: a number is required')
				replaceWith = Number(replace);
				break;
			case 'b':
				if(!type(replace, 'boolean')) throw('%b format: a boolean is required')
				replaceWith = Boolean(replace);
				break;
		}
		
		if(!global) find = new RegExp(find);
		return string.replace(find, replaceWith);
		
	}
	
	var ret = this;
		
	ret = ret.replace('%%', '%');
	
	// If data is empty
	if(typeof data == "undefined"){
		
	
	// If data is an array or array literal
	}else if(type(data, 'array')){
		
		var matches = this.match(/%[sifnb]/g);
		
		if(matches.length < data.length) throw('Not all arguments converted during string formatting');
		if(matches.length > data.length) throw('Not enough arguments for format string');
		
		for(var i = 0; i < matches.length; i++){
		    ret = doInterpolation(ret, matches[i], data[i], matches[i].replace('%', ''));
		}
	
	// If data is an object or object literal	
	}else if(type(data, 'object')){
		
		var matches = this.match(/%\([A-Za-z0-9_-]+\)([sifnb])/g);
		for(var i = 0; i < matches.length; i++){
			var name = matches[i].match(/\(([A-Za-z0-9_-]+)\)/)[1];
			var replType = matches[i].match(/([sifnb])$/)[1];
			ret = doInterpolation(ret, matches[i], data[name], replType, true);
		}
		
	}
	
	return ret;
	
}