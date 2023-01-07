package com.nkj.db;

import org.springframework.stereotype.Component;

@Component
public class MemberModel {
		
	  private int id;
	  private String email;
	  private String password;
	  
	  public MemberModel() {
		}
		
		public MemberModel(String email, String password) {
			super();
			this.email = email;
			this.password = password;
		}

		public MemberModel(int id, String email, String password) {
			super();
			this.id = id;
			this.email = email;
			this.password = password;
		}
	  
	  public int getId() {
		return id;
	  }
	  
	  public void setId(int id) {
		this.id = id;
	  }
	  public String getEmail() {
		return email;
	  }
	  
	  public void setEmail(String email) {
		this.email = email;
	  }
	  
	  public String getPassword() {
		return password;
	  }
	  
	  public void setPassword(String password) {
		this.password = password;
	  }

}