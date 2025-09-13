import json
import pandas as pd
from datetime import datetime, timedelta
import random
from collections import defaultdict, Counter
import numpy as np
from typing import List, Dict, Tuple

class PropertyChatRecommendationSystem:
    def __init__(self):
        # 定义问题分类和相关问题
        self.question_categories = {
            '报修管理': [
                '今天有多少个报修单',
                '报修单的处理进度怎么样',
                '紧急报修有哪些',
                '维修师傅联系方式',
                '报修历史记录',
                'B座电梯故障情况',
                '空调维修预约时间',
                '地下车库照明问题',
                '更新报修进度',
                '查看维修费用'
            ],
            '巡更监控': [
                '今天的巡更安排',
                '巡更人员当前位置',
                '巡更发现的异常情况',
                '夜间巡更计划',
                '巡更路线图',
                '消防门检查情况',
                '重点区域巡查',
                '巡更人员联系方式',
                '异常情况处理流程',
                '巡更质量评估'
            ],
            '保洁监督': [
                '今天的保洁任务',
                '保洁质量评分',
                '清洁人员安排',
                '大堂清洁情况',
                '地下车库清洁进度',
                '楼道保洁计划',
                '绿化维护安排',
                '垃圾清理时间',
                '清洁标准查看',
                '保洁投诉处理'
            ],
            '紧急事件': [
                '当前紧急情况',
                '电梯故障处理',
                '被困人员救援',
                '应急联系人',
                '事故报告生成',
                '通知住户公告',
                '安全警示设置',
                '应急预案启动',
                '现场情况汇报',
                '后续处理安排'
            ],
            '综合查询': [
                '今日待办事项',
                '今日待办事件',
                '工作统计报告',
                '人员工作安排',
                '设备运行状态',
                '住户反馈情况',
                '月度工作总结',
                '成本费用统计',
                '服务质量评估',
                '系统使用帮助',
                '联系管理员',
                '查看保修详情',
                '巡更路线图',
                '保洁质量报告',
                
            ]
        }
        
        # 定义问题间的关联规则
        self.question_transitions = {
            # 报修管理相关转换
            '今天有多少个报修单': ['报修单的处理进度怎么样', '紧急报修有哪些', '维修师傅联系方式'],
            '报修单的处理进度怎么样': ['更新报修进度', '维修师傅联系方式', 'B座电梯故障情况'],
            '紧急报修有哪些': ['B座电梯故障情况', '应急联系人', '被困人员救援'],
            'B座电梯故障情况': ['被困人员救援', '维修师傅联系方式', '通知住户公告'],
            
            
            
            # 巡更监控相关转换
            '今天的巡更安排': ['巡更人员当前位置', '夜间巡更计划', '巡更路线图'],
            '巡更人员当前位置': ['巡更发现的异常情况', '重点区域巡查', '异常情况处理流程'],
            '巡更发现的异常情况': ['消防门检查情况', '异常情况处理流程', '维修师傅联系方式'],
            
            # 保洁监督相关转换
            '今天的保洁任务': ['保洁质量评分', '清洁人员安排', '大堂清洁情况'],
            '保洁质量评分': ['清洁标准查看', '保洁投诉处理', '清洁人员安排'],
            '地下车库清洁进度': ['楼道保洁计划', '垃圾清理时间', '清洁人员安排'],
            
            # 综合查询相关转换
            '工作统计报告': ['服务质量评估', '成本费用统计', '月度工作总结'],
            '今日待办事项': ['查看保修详情', '巡更路线图', '保洁质量报告'],
            '查看保修详情': ['联系维修师傅', '更新进度', '查看历史记录'],
            '巡更路线图': ['实时位置追踪', '查看巡更路线', '异常情况处理'],
            '保洁质量报告': ['查看清洁标准', '质量检查报告', '人员调度'],
        }
        
        self.user_sessions = []
        self.generate_historical_data()
    
    def generate_historical_data(self, num_users=50, sessions_per_user=20):
        """生成历史会话数据"""
        print("正在生成历史会话数据...")
        
        user_profiles = {
            'property_manager': 0.3,    # 物业经理
            'maintenance_staff': 0.25,   # 维修人员
            'security_guard': 0.25,      # 保安
            'cleaning_staff': 0.2        # 保洁人员
        }
        
        # 不同角色的问题偏好
        role_preferences = {
            'property_manager': {
                '综合查询': 0.4, '报修管理': 0.25, '巡更监控': 0.2, '保洁监督': 0.15
            },
            'maintenance_staff': {
                '报修管理': 0.6, '紧急事件': 0.2, '综合查询': 0.15, '巡更监控': 0.05
            },
            'security_guard': {
                '巡更监控': 0.5, '紧急事件': 0.3, '综合查询': 0.15, '报修管理': 0.05
            },
            'cleaning_staff': {
                '保洁监督': 0.6, '综合查询': 0.25, '报修管理': 0.1, '巡更监控': 0.05
            }
        }
        
        for user_id in range(num_users):
            # 为用户分配角色
            role = np.random.choice(list(user_profiles.keys()), 
                                  p=list(user_profiles.values()))
            
            for session_id in range(sessions_per_user):
                session = {
                    'user_id': f'user_{user_id:03d}',
                    'session_id': f'session_{session_id:03d}',
                    'role': role,
                    'timestamp': datetime.now() - timedelta(days=random.randint(1, 90)),
                    'questions': []
                }
                
                # 生成会话中的问题序列 (3-8个问题)
                num_questions = random.randint(3, 8)
                
                # 确保分类和概率匹配
                categories = list(role_preferences[role].keys())
                probabilities = list(role_preferences[role].values())
                
                current_category = np.random.choice(categories, p=probabilities)
                
                for q_idx in range(num_questions):
                    if q_idx == 0:
                        # 第一个问题从偏好分类中选择
                        question = random.choice(self.question_categories[current_category])
                    else:
                        # 后续问题基于转换规则或随机选择
                        prev_question = session['questions'][-1]['content']
                        if prev_question in self.question_transitions:
                            # 80%概率按照转换规则，20%概率随机
                            if random.random() < 0.8:
                                question = random.choice(self.question_transitions[prev_question])
                            else:
                                question = random.choice(self.question_categories[current_category])
                        else:
                            question = random.choice(self.question_categories[current_category])
                    
                    session['questions'].append({
                        'question_id': q_idx,
                        'content': question,
                        'category': self._get_question_category(question),
                        'timestamp': session['timestamp'] + timedelta(minutes=q_idx*2)
                    })
                    
                    # 有30%概率切换到相关类别
                    if random.random() < 0.3:
                        current_category = self._get_related_category(current_category)
                
                self.user_sessions.append(session)
        
        print(f"已生成 {len(self.user_sessions)} 个会话，共包含用户 {num_users} 人")
    
    def _get_question_category(self, question):
        """获取问题所属分类"""
        for category, questions in self.question_categories.items():
            if question in questions:
                return category
        return '综合查询'
    
    def _get_related_category(self, current_category):
        """获取相关分类"""
        related_map = {
            '报修管理': ['紧急事件', '巡更监控'],
            '巡更监控': ['报修管理', '保洁监督'],
            '保洁监督': ['巡更监控', '综合查询'],
            '紧急事件': ['报修管理', '综合查询'],
            '综合查询': ['报修管理', '巡更监控', '保洁监督']
        }
        
        if current_category in related_map:
            return random.choice(related_map[current_category])
        return current_category
    
    def get_user_question_patterns(self, user_id: str) -> Dict:
        """获取用户的问题模式"""
        user_sessions = [s for s in self.user_sessions if s['user_id'] == user_id]
        
        if not user_sessions:
            return {}
        
        patterns = {
            'question_frequency': Counter(),
            'category_preference': Counter(),
            'transition_patterns': defaultdict(Counter),
            'session_patterns': [],
            'time_patterns': defaultdict(list)
        }
        
        for session in user_sessions:
            questions = [q['content'] for q in session['questions']]
            categories = [q['category'] for q in session['questions']]
            
            # 统计问题频率
            patterns['question_frequency'].update(questions)
            patterns['category_preference'].update(categories)
            
            # 统计转换模式
            for i in range(len(questions) - 1):
                patterns['transition_patterns'][questions[i]][questions[i+1]] += 1
            
            # 会话模式
            patterns['session_patterns'].append(questions)
            
            # 时间模式
            hour = session['timestamp'].hour
            patterns['time_patterns'][hour].extend(questions)
        
        return patterns
    
    def recommend_next_questions(self, user_id: str, current_question: str, 
                               top_k: int = 3) -> List[Tuple[str, float]]:
        """推荐下一个可能的问题"""
        # 获取用户历史模式
        user_patterns = self.get_user_question_patterns(user_id)
        
        if not user_patterns:
            # 新用户，使用全局模式
            return self._recommend_by_global_patterns(current_question, top_k)
        
        recommendations = defaultdict(float)
        
        # 1. 基于用户转换模式的推荐 (权重: 0.4)
        if current_question in user_patterns['transition_patterns']:
            for next_q, count in user_patterns['transition_patterns'][current_question].items():
                total_after_current = sum(user_patterns['transition_patterns'][current_question].values())
                recommendations[next_q] += 0.4 * (count / total_after_current)
        
        # 2. 基于全局转换规则的推荐 (权重: 0.3)
        if current_question in self.question_transitions:
            for next_q in self.question_transitions[current_question]:
                recommendations[next_q] += 0.3 * (1.0 / len(self.question_transitions[current_question]))
        
        # 3. 基于用户偏好的推荐 (权重: 0.2)
        current_category = self._get_question_category(current_question)
        related_questions = self.question_categories.get(current_category, [])
        for question in related_questions:
            if question != current_question:
                user_freq = user_patterns['question_frequency'].get(question, 0)
                total_questions = sum(user_patterns['question_frequency'].values())
                if total_questions > 0:
                    recommendations[question] += 0.2 * (user_freq / total_questions)
        
        # 4. 基于时间模式的推荐 (权重: 0.1)
        current_hour = datetime.now().hour
        if current_hour in user_patterns['time_patterns']:
            time_questions = Counter(user_patterns['time_patterns'][current_hour])
            total_time_questions = sum(time_questions.values())
            for question, count in time_questions.items():
                if question != current_question:
                    recommendations[question] += 0.1 * (count / total_time_questions)
        
        # 排序并返回top_k
        sorted_recommendations = sorted(recommendations.items(), 
                                      key=lambda x: x[1], reverse=True)
        
        # 如果推荐不足，补充全局推荐
        if len(sorted_recommendations) < top_k:
            global_recs = self._recommend_by_global_patterns(current_question, top_k * 2)
            for question, score in global_recs:
                if question not in recommendations:
                    sorted_recommendations.append((question, score * 0.1))
        
        return sorted_recommendations[:top_k]
    
    def _recommend_by_global_patterns(self, current_question: str, top_k: int) -> List[Tuple[str, float]]:
        """基于全局模式推荐"""
        recommendations = []
        
        # 基于预定义转换规则
        if current_question in self.question_transitions:
            score = 1.0
            for question in self.question_transitions[current_question]:
                recommendations.append((question, score))
                score -= 0.1  # 递减得分，体现优先级
        
        # 基于同类别问题
        current_category = self._get_question_category(current_question)
        category_questions = self.question_categories.get(current_category, [])
        for question in category_questions:
            if question != current_question and question not in [r[0] for r in recommendations]:
                recommendations.append((question, 0.5))
        
        # 基于相关类别问题
        related_category = self._get_related_category(current_category)
        if related_category != current_category:
            related_questions = self.question_categories.get(related_category, [])
            for question in related_questions[:3]:  # 只取前3个相关问题
                if question not in [r[0] for r in recommendations]:
                    recommendations.append((question, 0.3))
        
        # 按得分排序并返回
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    def analyze_user_behavior(self, user_id: str) -> Dict:
        """分析用户行为"""
        patterns = self.get_user_question_patterns(user_id)
        user_sessions = [s for s in self.user_sessions if s['user_id'] == user_id]
        
        if not patterns or not user_sessions:
            return {'error': '用户数据不存在'}
        
        analysis = {
            'user_id': user_id,
            'role': user_sessions[0]['role'] if user_sessions else 'unknown',
            'total_sessions': len(user_sessions),
            'total_questions': sum(patterns['question_frequency'].values()),
            'avg_questions_per_session': sum(patterns['question_frequency'].values()) / len(user_sessions),
            'most_frequent_questions': patterns['question_frequency'].most_common(5),
            'category_preferences': dict(patterns['category_preference']),
            'common_transitions': {}
        }
        
        # 分析常见转换
        for from_q, to_qs in patterns['transition_patterns'].items():
            if len(to_qs) > 0:
                analysis['common_transitions'][from_q] = to_qs.most_common(3)
        
        return analysis
    
    def demo_recommendation_system(self):
        """演示推荐系统"""
        print("=" * 60)
        print("物业管理AI助手 - 用户行为推荐系统演示")
        print("=" * 60)
        
        # 选择一个有足够数据的用户进行演示
        demo_user = 'user_001'
        
        # 分析用户行为
        print(f"\n📊 用户 {demo_user} 行为分析:")
        analysis = self.analyze_user_behavior(demo_user)
        print(f"用户角色: {analysis['role']}")
        print(f"总会话数: {analysis['total_sessions']}")
        print(f"总问题数: {analysis['total_questions']}")
        print(f"平均每会话问题数: {analysis['avg_questions_per_session']:.1f}")
        
        print(f"\n🔥 最频繁的问题:")
        for i, (question, count) in enumerate(analysis['most_frequent_questions'], 1):
            print(f"{i}. {question} (出现 {count} 次)")
        
        print(f"\n📋 分类偏好:")
        for category, count in analysis['category_preferences'].items():
            percentage = (count / analysis['total_questions']) * 100
            print(f"• {category}: {count} 次 ({percentage:.1f}%)")
        
        # 演示推荐功能
        print(f"\n" + "="*60)
        print("🎯 推荐系统演示")
        print("="*60)
        
        test_questions = [
            "今天有多少个报修单",
            "今天的巡更安排", 
            "今天的保洁任务",
            "当前紧急情况",
            "今天的待办"
        ]
        
        for current_question in test_questions:
            print(f"\n当前问题: 「{current_question}」")
            recommendations = self.recommend_next_questions(demo_user, current_question, 3)
            
            print("推荐的下一个问题:")
            for i, (question, score) in enumerate(recommendations, 1):
                print(f"{i}. {question} (置信度: {score:.3f})")
        
        # 展示实际会话示例
        print(f"\n" + "="*60)
        print("📝 实际会话示例")
        print("="*60)
        
        user_sessions = [s for s in self.user_sessions if s['user_id'] == demo_user]
        sample_session = random.choice(user_sessions)
        
        print(f"会话时间: {sample_session['timestamp'].strftime('%Y-%m-%d %H:%M')}")
        print("问题序列:")
        
        for i, question_info in enumerate(sample_session['questions'], 1):
            print(f"{i}. {question_info['content']} [{question_info['category']}]")
            
            if i < len(sample_session['questions']) - 1:
                # 显示推荐结果
                actual_next = sample_session['questions'][i]['content']
                recommendations = self.recommend_next_questions(demo_user, question_info['content'], 3)
                
                print(f"   → 系统推荐: {[r[0] for r in recommendations]}")
                print(f"   → 实际选择: 「{actual_next}」")
                
                # 检查推荐准确性
                recommended_questions = [r[0] for r in recommendations]
                if actual_next in recommended_questions:
                    rank = recommended_questions.index(actual_next) + 1
                    print(f"   ✅ 推荐命中 (排名第{rank})")
                else:
                    print(f"   ❌ 推荐未命中")
                print()

# 运行演示
if __name__ == "__main__":
    # 创建推荐系统实例
    system = PropertyChatRecommendationSystem()
    
    # 运行演示
    system.demo_recommendation_system()
    
    print(f"\n" + "="*60)
    print("💡 系统特性说明")
    print("="*60)
    print("1. 基于用户历史转换模式推荐 (权重40%)")
    print("2. 基于预定义规则推荐 (权重30%)")  
    print("3. 基于用户偏好推荐 (权重20%)")
    print("4. 基于时间模式推荐 (权重10%)")
    print("\n算法能够:")
    print("• 学习用户个人对话习惯")
    print("• 识别不同角色的问题偏好")
    print("• 根据上下文推荐相关问题")
    print("• 处理新用户的冷启动问题")
    print("• 实时调整推荐策略")