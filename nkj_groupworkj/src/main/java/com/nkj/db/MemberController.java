package com.nkj.db;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;


@RestController

public class MemberController {
	@Autowired
	MemberModel memberModel;
	@Autowired
	MemberRepository userDAO;
    

	@RequestMapping("/insertMember")
    public String hello(@RequestParam String[] data){
    	memberModel = new MemberModel();
    	memberModel.setEmail(data[0]);
    	memberModel.setPassword(data[1]);
    	userDAO.insert(memberModel);
        return "帳號創建成功";//重新登入
    }
    

    @RequestMapping("/sql")
    public String sql(@RequestParam String[] email){
    	memberModel = new MemberModel();
    	memberModel.setEmail(email[0]);
//    	MemberModel member=userDAO.selectMember(memberModel).get(0);   	
//    	return "您的密碼是:"+member.getPassword();
    	List<MemberModel> selectMember = userDAO.selectMember(memberModel);
        if (selectMember.size() > 0) {
        	return "您的密碼是:"+selectMember.get(0).getPassword();//成功 
        }else {
			return "查無此帳號";
		}
    }

    
}

