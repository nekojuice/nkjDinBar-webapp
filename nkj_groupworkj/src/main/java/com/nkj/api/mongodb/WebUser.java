package com.nkj.api.mongodb;

import com.mongodb.lang.NonNull;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;
import lombok.Data;

@Data //lomobok 省去get/set
@Document  //標記這個class對映一個collection，在(user)這個collection裡面操作document
public class WebUser {
    public WebUser(String id, String email, String userAccount, String userPassword, Integer depositAccount,
			Integer status) {
		super();
		this.id = id;
		this.email = email;
		this.userAccount = userAccount;
		this.userPassword = userPassword;
		this.depositAccount = depositAccount;
		this.status = status;
	}
	@Id
    private String id;  //這個id物件是對映每個document在被新增時都會有的_id
    @Indexed(unique = true)
    @NonNull
    private String email;
    @Indexed(unique = true)
    @NonNull
    private String userAccount;
    @NonNull
    private String userPassword;
    @NonNull
    private Integer depositAccount;
    @NonNull
    private Integer status;
}
