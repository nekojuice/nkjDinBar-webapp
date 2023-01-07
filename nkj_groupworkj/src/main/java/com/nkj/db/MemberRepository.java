package com.nkj.db;

import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;


@Repository
public class MemberRepository {
	@Autowired
	private JdbcTemplate jdbcTemplate;

	public int insert(MemberModel memberModel) {

		return jdbcTemplate.update(

				"INSERT INTO memberinfo (EMAIL,PASSWORD) VALUES (?,?)", memberModel.getEmail(),
				memberModel.getPassword());

	}

	public List<MemberModel> selectMember(MemberModel memberModel) {
		List<MemberModel> membermodel = new ArrayList<>();

		System.out.println("EXCUTE SELECT MEMBER");
		return jdbcTemplate.query("SELECT * FROM `memberinfo` WHERE `EMAIL`='" + memberModel.getEmail() + "'",
				new CustomerMapper());
	}

	private static final class CustomerMapper implements RowMapper<MemberModel> {

		public MemberModel mapRow(ResultSet rs, int rowNum) throws SQLException {

			return new MemberModel(

					rs.getInt("id"),

					rs.getString("email"),

					rs.getString("password")

			);

		}
	}
}