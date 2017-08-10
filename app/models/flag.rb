# == Schema Information
#
# Table name: flags
#
#  id      :integer          not null, primary key
#  name    :string
#  color   :string
#  resolve :boolean          default("false"), not null
#

class Flag < ApplicationRecord
  has_many :reviews, dependent: :destroy
end
